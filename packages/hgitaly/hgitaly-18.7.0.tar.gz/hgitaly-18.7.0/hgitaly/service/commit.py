# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
# Copyright 2021 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import itertools
import logging
import threading

from grpc import StatusCode
from google.protobuf.timestamp_pb2 import Timestamp
from mercurial import (
    error,
    pycompat,
    logcmdutil,
    hgweb,
    node as nodemod,
)

from hgext3rd.heptapod.branch import get_default_gitlab_branch

from .. import (
    message,
)
from ..errors import (
    not_implemented,
    structured_abort,
)
from ..logging import LoggerAdapter
from ..pagination import (
    extract_limit,
)
from ..revision import (
    VISIBLE_CHANGESETS,
    RevisionNotFound,
    gitlab_revision_changeset,
    resolve_revspecs_positive_negative,
)
from ..revset import (
    FollowNotImplemented,
    changeset_descr_regexp,
    revset_from_git_revspec,
)
from ..servicer import HGitalyServicer
from ..stream import (
    concat_resplit,
    WRITE_BUFFER_SIZE,
)
from ..stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitIsAncestorResponse,
    CheckObjectsExistRequest,
    CheckObjectsExistResponse,
    CountCommitsRequest,
    CountCommitsResponse,
    CountDivergingCommitsRequest,
    CountDivergingCommitsResponse,
    ListFilesRequest,
    ListFilesResponse,
    CommitStatsRequest,
    CommitStatsResponse,
    FindAllCommitsRequest,
    FindAllCommitsResponse,
    FindCommitsError,
    FindCommitsRequest,
    FindCommitsResponse,
    RawBlameError,
    RawBlameRequest,
    RawBlameResponse,
    CommitsByMessageRequest,
    CommitsByMessageResponse,
    ListCommitsRequest,
    ListCommitsResponse,
    FilterShasWithSignaturesRequest,
    FilterShasWithSignaturesResponse,
    GetCommitSignaturesRequest,
    GetCommitSignaturesResponse,
    GetCommitMessagesRequest,
    GetCommitMessagesResponse,
)
from ..stub.errors_pb2 import (
    PathNotFoundError,
)
from ..stub.commit_pb2_grpc import CommitServiceServicer
from ..util import (
    chunked,
    chunked_with_cursor,
)

base_logger = logging.getLogger(__name__)

NULL_REV = nodemod.nullrev
PSEUDO_REVS = (nodemod.wdirrev, nodemod.nullrev)
PSEUDO_REVLOG_NODES = {
    nodemod.nullid,
    nodemod.wdirid,
}
PSEUDO_REVLOG_NODES.update(nodemod.wdirfilenodeids)


class CommitServicer(CommitServiceServicer, HGitalyServicer):

    STATUS_CODE_STORAGE_NOT_FOUND = StatusCode.INVALID_ARGUMENT

    def CommitIsAncestor(self,
                         request: CommitIsAncestorRequest,
                         context) -> CommitIsAncestorResponse:
        logger = LoggerAdapter(base_logger, context)
        # The question is legit for filtered changesets and that
        # happens in MR rebase scenarios, before the Rails app realizes
        # the MR has to be updated.
        repo = self.load_repo(request.repository, context).unfiltered()
        # TODO status.Errorf(codes.InvalidArgument, "Bad Request
        # (empty ancestor sha)") and same for child
        try:
            ancestor = repo[request.ancestor_id.encode()]
            child = repo[request.child_id.encode()]
        except (error.RepoLookupError, error.ProgrammingError) as exc:
            # Gitaly just returns False. This is probably an inconsistency
            # in the client, so let's log it to help.
            logger.warning(
                "CommitIsAncestor for child_id=%r, ancestor_id=%r, got %r",
                request.ancestor_id, request.child_id, exc)
            result = False
        else:
            result = ancestor.isancestorof(child)

        return CommitIsAncestorResponse(value=result)

    def CountCommits(self,
                     request: CountCommitsRequest,
                     context) -> CountCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        # TODO: yet to finish this method to support all lookups
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        # revision can be a pseudo range, like b'12340f9b5..a5f36b6a53012',
        # (see CommitsBetween for how we handle that)
        # (used in MR widget)
        if revision:
            if b'..' in revision:
                # TODO also case of ... (3 dots), I suppose
                ctx_start, ctx_end = [gitlab_revision_changeset(repo, rev)
                                      for rev in revision.split(b'..')]
                if ctx_start is None or ctx_end is None:
                    logger.warning(
                        "CountCommits for %r: one of these revisions "
                        "could not be found", revision)
                    return CountCommitsResponse()

                if ctx_end.obsolete() or ctx_start.obsolete():
                    repo = repo.unfiltered()

                revs = repo.revs('only(%s, %s)',
                                 ctx_end.hex(), ctx_start.hex())
            else:
                ctx = gitlab_revision_changeset(repo, revision)
                if ctx is None:
                    logger.warning(
                        "CountCommits revision %r could not be found",
                        revision)
                    return CountCommitsResponse()
                revs = repo.unfiltered().revs('::%s', ctx)
            count = len(revs)
        elif not request.all:
            # note: `revision` and `all` are mutually exclusive
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "empty Revision and false All")
        else:
            # Note: if revision is not passed, we return all revs for now.
            # TODO not really exact, should be non obsolete and ::keeparounds
            count = len(repo)
        max_count = request.max_count
        if max_count and count > max_count:
            # TODO better to limit the revsets before hand
            count = max_count
        return CountCommitsResponse(count=count)

    # CountDivergingCommits counts the diverging commits between from and to.
    # Important to note that when --max-count is applied, the counts are not
    # guaranteed to be accurate.

    def CountDivergingCommits(self,
                              request: CountDivergingCommitsRequest,
                              context) -> CountDivergingCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        rev_from = gitlab_revision_changeset(repo, getattr(request, 'from'))
        rev_to = gitlab_revision_changeset(repo, getattr(request, 'to'))
        max_count = request.max_count
        if rev_from is None:
            logger.warning("cannot resolve 'from' revision in %r",
                           message.Logging(request))
        if rev_to is None:
            logger.warning("cannot resolve 'to' revision in %r",
                           message.Logging(request))
        if rev_from is None or rev_to is None:
            return CountDivergingCommitsResponse(left_count=0, right_count=0)
        left = rev_from.rev()
        right = rev_to.rev()

        # Switching to unfiltered repo view, only if really needed.
        # using the unfiltered repo should not change the result given that
        # the revisions are fully resolved, but let's not take the risk.
        if rev_from.obsolete() or rev_to.obsolete():
            repo = repo.unfiltered()

        branchpoint = repo.revs(b"ancestor(%d, %d)" % (left, right)).first()
        if branchpoint is None:
            left_revset = b'::%d' % left
            right_revset = b'::%d' % right
        else:
            left_revset = b"%d::%d - %d" % (branchpoint, left, branchpoint)
            right_revset = b"%d::%d  - %d" % (branchpoint, right, branchpoint)
        left_count = len(repo.revs(left_revset))
        right_count = len(repo.revs(right_revset))

        if max_count and (left_count + right_count) > max_count:
            delta = (left_count + right_count) - max_count
            if left_count >= delta:
                left_count -= delta
            else:
                delta -= left_count
                left_count = 0
                right_count -= delta
        return CountDivergingCommitsResponse(left_count=left_count,
                                             right_count=right_count)

    def ListFiles(self, request: ListFilesRequest,
                  context) -> ListFilesResponse:
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        mf = ctx.manifest()
        for paths in chunked(mf.iterkeys()):
            yield ListFilesResponse(paths=paths)

    def CommitStats(self, request: CommitStatsRequest,
                    context) -> CommitStatsResponse:
        repo = self.load_repo(request.repository, context)
        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            context.abort(StatusCode.INTERNAL,
                          "failed to get commit stats: object not found.")

        ctxp1 = ctx.p1()
        statsgen = hgweb.webutil.diffstatgen(repo.ui, ctx, ctxp1)
        # stats format:
        #   (list_of_stats_per_file, maxname,
        #    maxtotal, addtotal, removetotal, binary)
        # we only need addtotal and removetotal for our use case
        stats = next(statsgen)
        addtotal, removetotal = stats[-3], stats[-2]
        return CommitStatsResponse(
            oid=ctx.hex(),
            additions=addtotal,
            deletions=removetotal,
        )

    def FindAllCommits(self, request: FindAllCommitsRequest,
                       context) -> FindAllCommitsResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        revision = request.revision
        if revision:
            # If false, return all commits reachable by any branch in the repo
            ctx = gitlab_revision_changeset(repo, revision)
            if ctx is None:
                logger.warning(
                    "FindAllCommits revision %r could not be found",
                    revision)
                return FindAllCommitsResponse()
            revset = b"reverse(::%s)" % ctx
            # if ctx is an obsolete changeset, its repo is unfiltered.
            # this is legitimate if revision is a direct hash or a GitLab
            # special ref and should not happen otherwise
            repo = ctx.repo()
        else:
            revset = b'reverse(all())'

        revs = repo.revs(revset)
        offset = request.skip
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        if request.max_count:
            revs = revs.slice(0, request.max_count)
        if request.order == FindAllCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
        elif request.order == FindAllCommitsRequest.DATE:
            revs = repo.revs(b"reverse(sort(%ld, date))", revs)
        for chunk in chunked(revs):
            yield FindAllCommitsResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def FindCommits(self, request: FindCommitsRequest,
                    context) -> FindCommitsResponse:

        logger = LoggerAdapter(base_logger, context)
        req_log = message.Logging(request)
        stop_event = threading.Event()

        if request.limit == 0:
            return

        def on_rpc_done():
            stop_event.set()

        context.add_callback(on_rpc_done)

        repo = self.load_repo(request.repository, context)
        pats = request.paths
        # XXX: raise error if one of the path given is an empty string
        if pats:
            pats = list(map(lambda p: repo.root + b'/' + p, pats))

        repo, opts = parse_find_commits_request_opts(request, context, repo)

        if request.revision and not opts[b'rev'][0]:
            logger.debug(
                "Request %r, revision could not be found", req_log)
            structured_abort(
                context, StatusCode.NOT_FOUND, "commits not found",
                FindCommitsError())

        message_regex = request.message_regex
        if message_regex:
            grep = f" and grep('(?i){message_regex}')"
            opts[b'rev'][0] += grep.encode('utf-8')

        walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
        revs, _ = logcmdutil.getrevs(repo, walk_opts)

        if stop_event.is_set():  # pragma no cover (hard to test)
            logger.info("Request %r cancelled!", req_log)
            return

        if request.offset > 0:
            revs = revs.slice(request.offset, len(revs))

        if request.order == FindCommitsRequest.TOPO:
            revs = repo.revs(b"sort(%ld, topo)", revs)
            if request.all:
                revs = repo.revs(b"reverse(%ld)", revs)

        # investigation log for heptapod#1365
        if len(revs) == 0:
            logger.info("Empty commit list for walk_opts=%r", walk_opts)
#            context.abort(StatusCode.NOT_FOUND, "commits not found")

        incl_ref_by = request.include_referenced_by

        with_short_stats = request.include_shortstat
        for chunk in chunked(revs):
            if stop_event.is_set():  # pragma no cover (hard to test)
                logger.info("Request %r cancelled!", req_log)
                return

            yield FindCommitsResponse(
                commits=(message.commit(repo[rev],
                                        include_referenced_by=incl_ref_by,
                                        with_short_stats=with_short_stats)
                         for rev in chunk))

    def RawBlame(self, request: RawBlameRequest,
                 context) -> RawBlameResponse:
        repo = self.load_repo(request.repository, context)
        filepath = request.path
        if not filepath:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty Path")

        if request.range:
            lstart, lend = [int(x) for x in request.range.split(b',')]
            lstart -= 1
        else:
            lstart, lend = 0, None

        revision = pycompat.sysbytes(request.revision)
        ctx = gitlab_revision_changeset(repo, revision)
        if ctx is None:
            return
        try:
            for data in concat_resplit(blamelines(repo, ctx, filepath,
                                                  lstart=lstart,
                                                  lend=lend,
                                                  ),
                                       WRITE_BUFFER_SIZE):
                yield RawBlameResponse(data=data)
        except error.ManifestLookupError:
            structured_abort(
                context, StatusCode.NOT_FOUND,
                "path not found in revision",
                RawBlameError(path_not_found=PathNotFoundError(path=filepath))
            )
        except BlameRangeError as exc:
            structured_abort(
                context,
                StatusCode.INVALID_ARGUMENT,
                "range is outside of the file length",
                RawBlameError(out_of_range=RawBlameError.OutOfRangeError(
                    actual_lines=exc.actual_lines())))

    def CommitsByMessage(self, request: CommitsByMessageRequest,
                         context) -> CommitsByMessageResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context)
        query = request.query
        if not query:
            return CommitsByMessageResponse()
        pats = []
        opts = {}
        if request.path:
            path = repo.root + b'/' + request.path
            pats.append(path)
        if request.limit:
            opts[b'limit'] = request.limit
        if request.revision:
            revset = revset_from_git_revspec(repo, request.revision)
            repo = repo.unfiltered()
            if revset is None:
                logger.debug(
                    "CommitsByMessage revision %r could not be found",
                    request.revision)
                return CommitsByMessageResponse()
        else:
            revision = get_default_gitlab_branch(repo)
            # XXX: return error if no default branch found
            revset = revset_from_git_revspec(repo, revision)
        # Instead of sending 'query' as a key:value pair ('keyword': query) in
        # `opts`, appending the query to `revset` as "...and keyword('query')"
        # to make sure it perform an intersetion of two, instead of a union.
        revset = revset + b" and keyword('%b')" % query.encode()
        opts[b'rev'] = [revset]
        walk_opts = logcmdutil.parseopts(repo.ui, pats, opts)
        revs, _ = logcmdutil.getrevs(repo, walk_opts)
        offset = request.offset
        if offset and offset > 0:
            revs = revs.slice(offset, len(revs))
        for chunk in chunked(revs):
            yield CommitsByMessageResponse(
                commits=(message.commit(repo[rev]) for rev in chunk))

    def CheckObjectsExist(self, request: CheckObjectsExistRequest,
                          context) -> CheckObjectsExistResponse:
        not_implemented(context, issue=101)  # pragma no cover

    def ListCommits(self, request: ListCommitsRequest,
                    context) -> ListCommitsResponse:
        """Implementation of ListCommits, with some differences with Gitaly.

        Orderings
        ~~~~~~~~~
        As recalled in `commit.proto` comment, Git default ordering (and
        hence Gitaly's) is by date BUT that means actually first by
        parentship, then by date (actually CommitDate, not AuthorDate).
        Quoting git-log(1):

         --date-order
             Show no parents before all of its children are shown, but
             otherwise show commits in the commit timestamp order.

        I could check that this commit timestamp is the `CommitDate` field.

        On the other hand, Mercurial's date ordering ignores
        the graph completely, and there's no mixed ordering similar to Git's
        (although perhaps the `topo.firstbranch` could be used for this.

        NONE (default)
        --------------
        By default, instead of Git's (parentship, CommitDate) we're using
        the rev number: it respects parentship, and is conceptually close
        to the CommitDate ordering, which is by default the actual date of
        this exact commit creation (for instance, it is updated by
        `git commit --amend` whereas AuthodDate is not). CommitDate can be
        forced on a Git repository, but there's no Mercurial equivalent of
        that. The end result will be something akin to a PushDate field if
        there was any.

        There is hopefully no logic that really depends on the ordering on
        the client side, as long as it respects the parentship. As of this
        writing, this call is used for Merge Requests list of commits.
        Respecting the parentship is important, CommitDate on the Git side
        vs PushDate on the Mercurial side is probably not.

        TOPO
        ----

        These behave the same way between Git and Mercurial, the client
        will have to consider the choice of parent to present first to
        be arbitrary anyway

        DATE
        ----

        As explained above, Mercurial's date ordering is quite different
        from Git's. For now we choose to use it nevertheless if explicitely
        requested, but this could change if we identify trouble.
        """
        revisions = request.revisions
        if not revisions:
            context.abort(StatusCode.INVALID_ARGUMENT, "missing revisions")

        repo = self.load_repo(request.repository, context)
        revisions = (pycompat.sysbytes(r) for r in revisions)
        try:
            positive, negative = resolve_revspecs_positive_negative(
                repo, revisions)
        except RevisionNotFound as exc:
            context.abort(StatusCode.INTERNAL,
                          "Revision %r could not be resolved" % exc.args[0])

        walk = not request.disable_walk

        if positive is VISIBLE_CHANGESETS:
            # do not switch to unfiltered view!
            if negative:
                revset = b'not ::%ls'
            else:
                revset = b'all()'
        else:
            # now that resolution is done, we can and have to switch to
            # the unfiltered view, because the resulting hashes can be of
            # obsolete changesets.
            repo = repo.unfiltered()
            if negative:
                revset = b'only(%ls, %ls)'
            elif walk:
                revset = b'::%ls'
            else:
                revset = b'%ls'

        msg_patterns = request.commit_message_patterns
        ignore_case = request.ignore_case
        if msg_patterns:
            # TODO all kinds of painful escapings (should be in lib)
            greps = [changeset_descr_regexp(pattern, ignore_case=ignore_case)
                     for pattern in msg_patterns]
            if len(greps) > 1:
                revset += b' and (%s)' % b' or '.join(greps)
            else:
                revset += b' and ' + greps[0]

        after = request.after.ToSeconds()
        before = request.before.ToSeconds()
        date = getdate(after, before)
        if date is not None:
            revset += b" and date('%s')" % date.encode('ascii')

        author = request.author
        if author:
            revset += b" and user(r're:%s')" % author

        # no octopuses in Mercurial, hence max_parents > 1 does not filter
        # anything
        if request.max_parents == 1:
            revset += b" and not merge()"

        if request.paths:
            revset += b" and ("
            revset += b" or ".join(
                b'file("%s/%s")' % (repo.root, p)
                for p in request.paths
            )
            revset += b")"

        Order = ListCommitsRequest.Order
        reverse = request.reverse

        if request.order == Order.NONE:
            # default Git ordering is Mercurial's reversed
            sort_key = b'rev' if reverse else b'-rev'
        elif request.order == Order.TOPO:
            sort_key = b'-topo' if reverse else b'topo'
        elif request.order == Order.DATE:
            # See docstring about this approximative choice
            sort_key = b'date' if reverse else b'-date'

        revset = b'sort(%s, %s)' % (revset, sort_key)

        try:
            if positive is VISIBLE_CHANGESETS:
                if negative:
                    revs = repo.revs(revset, negative)
                else:
                    revs = repo.revs(revset)
            elif negative:
                revs = repo.revs(revset, positive, negative)
            else:
                revs = repo.revs(revset, positive)
        except error.ParseError as exc:
            # no point trying to mimic Gitaly's error message, as it is
            # very dependent on internal details. Example for invalid regexp
            # with Gitaly 15.4:
            #  iterating objects: re...e command: exit status 128,
            #  stderr: "fatal: command line, '[]': Unmatched [, [^, [:, [.,
            #  or [=\n"
            context.abort(StatusCode.INTERNAL, "Invalid filter: " + str(exc))

        # `skip` has to be interpreted before pagination
        # smartset.slice insists on having a "last" value:
        # it constructs a list internally, which would be a performance
        # issue to skip the first 3 revisions of a million-sized revset.
        # Too bad there is no cheap way to consume the revset as an iterator.
        # Anyway we'd do that in a Rust implementation if ever needed.
        if request.skip > 0:
            revs = revs.slice(request.skip, len(revs))

        # according to protocol comment, the page token
        # is the last commit OID already sent (similar to blob/tree requests)
        cursor = request.pagination_params.page_token
        if not cursor:
            offset = 0
        else:
            # TODO perf it would probably be much faster to use the index
            # directly rather than to construct contexts
            for offset, rev in enumerate(revs):
                sha = repo[rev].hex().decode()
                if sha == cursor:
                    offset = offset + 1
                    break
        limit = extract_limit(request)
        revs = revs.slice(offset, offset + limit)
        if not revs:
            return

        next_cursor = repo[revs.last()].hex().decode()
        yield from chunked_with_cursor(
                ListCommitsResponse,
                revs,
                next_cursor=next_cursor,
                builder=lambda chunk: dict(
                    commits=(message.commit(repo[rev]) for rev in chunk)
                )
        )

    def FilterShasWithSignatures(self,
                                 request: FilterShasWithSignaturesRequest,
                                 context) -> FilterShasWithSignaturesResponse:
        not_implemented(context, issue=24)  # pragma no cover

    def GetCommitSignatures(self, request: GetCommitSignaturesRequest,
                            context) -> GetCommitSignaturesResponse:
        not_implemented(context, issue=24)  # pragma no cover

    def GetCommitMessages(self, request: GetCommitMessagesRequest,
                          context) -> GetCommitMessagesResponse:
        repo = self.load_repo(request.repository, context)
        results = {}
        for commit_id in request.commit_ids:
            commit_id = pycompat.sysbytes(commit_id)
            ctx = gitlab_revision_changeset(repo, commit_id)
            if ctx is None:
                # should not be an "internal" error, but
                # that's what Gitaly does anyway
                context.abort(
                    StatusCode.INTERNAL,
                    "failed to get commit message: object not found.")

            results[commit_id] = ctx.description()
        for commit_id, msg in results.items():
            yield GetCommitMessagesResponse(commit_id=commit_id,
                                            message=msg)


def parse_find_commits_request_opts(request, context, repo):
    """Interpred FindCommitRequestAttributes

    :return: (repo, options for logcmdutil.parseopts). Returning the repo
      is important because we often (but not always) need to switch to
      the unfiltered repo.
    """
    logger = LoggerAdapter(base_logger, context)
    opts = {
        b'follow': request.follow,
        b'no_merges': request.skip_merges,
        b'limit': request.limit + request.offset,
    }
    # TODO: implement 'request.first_parent' option
    # khanchi97: found that its counterpart follow-first in "hg log" is
    # deprecated and give wrong results with other options like revision,
    # all, etc.
    if request.author:
        opts[b'user'] = [request.author]
    after = request.after.ToSeconds()
    before = request.before.ToSeconds()
    date = getdate(after, before)
    if date is not None:
        opts[b'date'] = date

    revision = request.revision
    # `revision` and `all` are mutually exclusive,
    # if both present `all` gets the precedence
    if request.all:
        opts[b'rev'] = [b'0:tip']
        return repo, opts

    if not revision:
        revision = get_default_gitlab_branch(repo)

    if revision:
        try:
            revset = revset_from_git_revspec(repo, revision,
                                             for_follow=request.follow)
        except FollowNotImplemented:
            logger.warning("Ignoring `follow: true` (not implemented with "
                           "this revspec) for %r", message.Logging(request))
            revset = revset_from_git_revspec(repo, revision)
            opts[b'follow'] = False

        opts[b'rev'] = [revset]
    return repo.unfiltered(), opts


def getdate(after, before):
    if after and before:
        after = _isoformat_from_seconds(after)
        before = _isoformat_from_seconds(before)
        return "%s UTC to %s UTC" % (after, before)
    elif after:
        after = _isoformat_from_seconds(after)
        return ">%s UTC" % after
    elif before:
        before = _isoformat_from_seconds(before)
        return "<%s UTC" % before
    return None


def _isoformat_from_seconds(secs):
    ts = Timestamp()
    ts.FromSeconds(int(secs))
    dt = ts.ToDatetime()
    return dt.isoformat()


class BlameRangeError(RuntimeError):
    def actual_lines(self):
        return self.args[0]


def blamelines(repo, ctx, file, lstart=0, lend=None):
    """Yield blame lines of a file.
    """
    fctx = ctx[file]
    # fctx.annotate() does not seem to be able to be linited to
    # a range, and is not even an iterator (as of Mercurial 6.6).
    # All we can do is use islice for the day it would become an iterator.
    # so that, e.g.,  annotating only the first line of a very large file
    # is less expensive than annotating the whole
    annotated = fctx.annotate()
    if lstart >= len(annotated):
        raise BlameRangeError(len(annotated))

    for line_no, line in enumerate(
            itertools.islice(fctx.annotate(), lstart, lend),
            start=1):
        old_line_no = line.lineno
        # required blame line format that get parsed by Rails:
        #   '<hash_id> <old_line_no> <line_no>\n\t<line_text>'
        yield b'%s %d %d\n\t%s' % (line.fctx.hex(), old_line_no, line_no,
                                   line.text)
