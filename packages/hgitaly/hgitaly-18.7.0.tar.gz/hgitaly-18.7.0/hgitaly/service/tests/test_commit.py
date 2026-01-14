# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest
import time
from mercurial import (
    pycompat,
)
from mercurial_testhelpers import (
    as_bytes,
)
from google.protobuf.timestamp_pb2 import Timestamp
from hgext3rd.heptapod.branch import (
    set_default_gitlab_branch,
    write_gitlab_branches,
)
from hgext3rd.heptapod.branch import (
    write_gitlab_tags,
)
from hgext3rd.heptapod.special_ref import (
    write_special_refs,
)

from hgitaly.tests.common import (
    make_empty_repo,
    make_tree_shaped_repo,
)

from hgitaly.stub.commit_pb2 import (
    CommitIsAncestorRequest,
    CommitsByMessageRequest,
    CommitStatsRequest,
    CountCommitsRequest,
    CountDivergingCommitsRequest,
    FindCommitsRequest,
    FindAllCommitsRequest,
    GetCommitMessagesRequest,
    ListCommitsRequest,
    ListFilesRequest,
    RawBlameRequest,
)
from hgitaly.stub.commit_pb2_grpc import CommitServiceStub

from hgitaly.stub.shared_pb2 import (
    CommitStatInfo,
    PaginationParameter,
)

from .fixture import ServiceFixture


class CommitFixture(ServiceFixture):

    stub_cls = CommitServiceStub

    def is_ancestor(self, hex1, hex2):
        return self.stub.CommitIsAncestor(
            CommitIsAncestorRequest(repository=self.grpc_repo,
                                    ancestor_id=hex1,
                                    child_id=hex2,
                                    )
        ).value

    def find_commits(self, limit=10, **opts):
        request = FindCommitsRequest(repository=self.grpc_repo,
                                     limit=limit, **opts)
        resp = self.stub.FindCommits(request,
                                     metadata=self.grpc_metadata())
        return [commit for chunk in resp for commit in chunk.commits]

    def find_commits_ids(self, **kwargs):
        return [commit.id.encode('ascii')
                for commit in self.find_commits(**kwargs)]

    def find_commits_stats(self, **kwargs):
        return [commit.short_stats
                for commit in self.find_commits(include_shortstat=True,
                                                **kwargs)
                ]

    def count_commits(self, revision, **kwargs):
        kwargs.setdefault('repository', self.grpc_repo)
        if revision is not None:
            kwargs['revision'] = revision
        return self.rpc('CountCommits', CountCommitsRequest(**kwargs)).count

    def list_commits_with_cursor(self, *revisions,
                                 limit=None,
                                 page_token=None,
                                 **kw):
        if limit is None and page_token is None:
            pagination = None
        else:
            pagination = PaginationParameter(limit=limit,
                                             page_token=page_token)

        request = ListCommitsRequest(repository=self.grpc_repo,
                                     revisions=revisions,
                                     pagination_params=pagination,
                                     **kw,
                                     )

        responses = self.stub.ListCommits(request)
        commit_ids = []
        cursor = None
        for resp in responses:
            commit_ids.extend(c.id.encode('ascii') for c in resp.commits)
            if resp.HasField('pagination_cursor'):
                cursor = resp.pagination_cursor.next_cursor.encode('ascii')
        return commit_ids, cursor

    def list_commits(self, *args, **kwargs):
        return self.list_commits_with_cursor(*args, **kwargs)[0]


@pytest.fixture
def commit_fixture_empty_repo(grpc_channel, server_repos_root):
    with CommitFixture(grpc_channel,
                       server_repos_root,
                       ) as fixture:
        yield fixture


@pytest.fixture
def commit_fixture_tree_shaped_repo(grpc_channel, server_repos_root):
    with CommitFixture(grpc_channel,
                       server_repos_root,
                       repo_factory=make_tree_shaped_repo,
                       ) as fixture:
        yield fixture


def test_is_ancestor(commit_fixture_tree_shaped_repo):
    fixture = commit_fixture_tree_shaped_repo
    changesets = fixture.changesets

    def is_ancestor(key1, key2):
        return fixture.is_ancestor(changesets[key1].hex(),
                                   changesets[key2].hex())

    assert is_ancestor('base', 'top1')
    assert not is_ancestor('other_base', 'default')
    assert is_ancestor('default', 'default')
    assert is_ancestor('other_base', 'wild2')

    base_hex = changesets['base'].hex()
    # id in message *has* logically to be 40 chars
    # technically, on current Mercurial if short_id is str, repo[short_id]
    # does not work but repo[full_id] does.
    unknown_hex = '1234dead' * 5

    assert fixture.is_ancestor(base_hex, unknown_hex) is False
    assert fixture.is_ancestor(unknown_hex, base_hex) is False


def test_is_ancestor_obsolete(commit_fixture_tree_shaped_repo):
    fixture = commit_fixture_tree_shaped_repo
    wrapper = fixture.repo_wrapper

    # still works if one of the changesets becomes obsolete
    ctx1 = wrapper.commit_file('foo')
    ctx2 = wrapper.commit_file('foo2')

    wrapper.command('amend', message=b'amended')
    assert fixture.is_ancestor(ctx1.hex(), ctx2.hex())


def test_find_commits(commit_fixture_empty_repo):
    fixture = commit_fixture_empty_repo
    fixture.correlation_id = "2222-correlation"
    wrapper = fixture.repo_wrapper
    find_commits_ids = fixture.find_commits_ids
    # set default branch
    set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # prepare repo as:
    #
    #   @    4 (branch/default) merge with stable
    #   |\
    #   | o  3 creates 'animal' (branch/stable)
    #   | |
    #   o |  2 rename 'foo' to 'zoo' (user: testuser2)
    #   |/
    #   | 1 changes 'foo'
    #   |/
    #   o  0  creates 'foo'
    #

    ctx0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('foo')
    wrapper.update(0)
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ctx2 = wrapper.commit([b'foo', b'zoo'], message=b"rename foo to zoo")
    # commits with different date/time, to test with date filter later
    timestamp = int(time.time())
    ctx3 = wrapper.commit_file('animals', branch='stable', parent=ctx0,
                               utc_timestamp=timestamp+10, user='testuser2')
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable',
                                utc_timestamp=timestamp+20)
    sha0, sha1, sha2, sha3, sha4 = (ctx0.hex(), ctx1.hex(), ctx2.hex(),
                                    ctx3.hex(), ctx4.hex())
    # symbolic revision
    assert find_commits_ids(revision=b'branch/stable') == [sha3, sha0]
    # with follow; test that it follows renames
    assert find_commits_ids(paths=[b'zoo'], follow=True) == [sha2, sha0]
    # with follow and Git Range Notation, it does not **currently** follow
    # (see hgitaly#117)
    assert find_commits_ids(revision=b'2...3', paths=[b'zoo'],
                            follow=True) == [sha2]
    # with revision
    assert find_commits_ids(revision=b'4...1') == [sha4, sha3, sha2, sha1]
    assert find_commits_ids(revision=b'0..4') == [sha4, sha3, sha2]
    # use default branch if any of the side is omitted
    assert find_commits_ids(revision=b'...1') == [sha4, sha3, sha2, sha1]
    assert find_commits_ids(revision=b'1...') == [sha4, sha3, sha2, sha1]
    assert find_commits_ids(revision=b'0..') == [sha4, sha3, sha2]
    assert find_commits_ids(revision=b'..0') == []
    # when revision does not exists (including special Node IDs)
    for rev in (b'does_not_exists',
                b'1234deadbeaf',
                b'ffffffff' * 5,
                b'ffffffff'):
        with pytest.raises(grpc.RpcError) as exc_info:
            find_commits_ids(revision=rev)
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    # with all, return all the commits
    assert find_commits_ids(all=True) == [sha0, sha1, sha2, sha3, sha4]
    # with message_regex
    assert find_commits_ids(all=True, message_regex='FOO.*zoO') == [sha2]
    # with offset
    assert find_commits_ids(all=True, offset=2) == [sha2, sha3, sha4]
    # with skip_merges
    assert find_commits_ids(skip_merges=True) == [sha3, sha2, sha0]
    # with short stats
    assert fixture.find_commits_stats(revision=sha1) == [
        CommitStatInfo(additions=2, deletions=2, changed_files=1),
        CommitStatInfo(additions=3, changed_files=1),
    ]
    assert not fixture.find_commits(revision=sha4,
                                    limit=1,
                                    include_shortstat=True
                                    )[0].HasField('short_stats')

    # with date specs
    date, date2 = Timestamp(), Timestamp()
    date.FromSeconds(timestamp+10)
    assert find_commits_ids(before=date) == [sha3, sha2, sha0]
    assert find_commits_ids(after=date) == [sha4, sha3]
    # gracinet: given that before is < and after is > I didn't expect
    # after=before to return anything, but `hg help dates` says that
    # the `to` range specifier is inclusive.
    assert find_commits_ids(after=date, before=date) == [sha3]
    date2.FromSeconds(timestamp+100)
    assert find_commits_ids(after=date, before=date2) == [sha4, sha3]

    # with pats, return commits containing changes to pats
    assert find_commits_ids(paths=[b'foo', b'animals']) == [sha3, sha0]
    # when no revision passed; return revs("reverse(::default_tip)")
    assert find_commits_ids() == [sha4, sha3, sha2, sha0]
    # with limit
    assert find_commits_ids(limit=0) == []
    assert find_commits_ids(limit=2) == [sha4, sha3]
    # with author
    assert find_commits_ids(all=True, author=b"testuser2") == [sha3]
    # with order
    ctx5 = wrapper.commit_file('foo', parent=ctx1)
    sha5 = ctx5.hex()
    assert find_commits_ids(all=True, order=FindCommitsRequest.Order.TOPO) == [
        sha0, sha2, sha3, sha4, sha1, sha5]
    # with include_referenced_by
    assert fixture.find_commits(  # without state files empty instead of crash
        revision=sha3,
        include_referenced_by=[b'refs']
    )[0].referenced_by == []
    write_gitlab_branches(wrapper.repo, {b'branch/stable': sha3})
    assert fixture.find_commits(
        revision=sha3,
        include_referenced_by=[b'refs']
    )[0].referenced_by == [b'refs/heads/branch/stable']
    assert fixture.find_commits(
        revision=sha3,
        include_referenced_by=[b'refs/tags']
    )[0].referenced_by == []
    write_gitlab_tags(wrapper.repo, {b'release': sha3})
    assert fixture.find_commits(
        revision=sha3,
        include_referenced_by=[b'refs/tags']
    )[0].referenced_by == [b'refs/tags/release']
    write_special_refs(wrapper.repo, {b'pipelines/12': sha3})
    assert fixture.find_commits(
        revision=sha3,
        include_referenced_by=[b'refs/pipelines/']
    )[0].referenced_by == [b'refs/pipelines/12']
    set_default_gitlab_branch(wrapper.repo, b'branch/stable')
    assert fixture.find_commits(
        revision=sha3,
        include_referenced_by=[b'HEAD', b'refs/heads']
    )[0].referenced_by == [b'refs/heads/branch/stable', b'HEAD']

    # test with direct tag as revision (cannot use the 'release' tag
    # on sha3 because it is not a full Mercurial tag).
    wrapper.command('tag', b'v3.2.1', rev=sha3)
    assert find_commits_ids(revision=b'v3.2.1', limit=1) == [sha3]

    # tests with obsolete changesets
    wrapper.amend_file('foo')
    assert find_commits_ids(revision=sha5) == [sha5, sha1, sha0]


def test_commits_by_message(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    set_default_gitlab_branch(wrapper.repo, b'branch/default')
    # repo structure:
    #
    #   o 2 add animal (branch/stable)
    #   |
    #   | 1 add bar
    #   |/
    #   o 0 add foo
    #

    def do_rpc(**opts):
        request = CommitsByMessageRequest(repository=grpc_repo, **opts)
        resp = grpc_stub.CommitsByMessage(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]
    ctx0 = wrapper.commit_file('foo', message=b'add foo')
    ctx1 = wrapper.commit_file('bar', parent=ctx0, message=b'add bar')
    ctx2 = wrapper.commit_file('animal', branch='stable', parent=ctx0,
                               message=b'add animal')
    sha0, sha1, sha2 = ctx0.hex(), ctx1.hex(), ctx2.hex()

    # without revision; use default branch set in repo config
    assert do_rpc(query=b'add') == [sha1, sha0]
    assert do_rpc(query=b'bar') == [sha1]
    assert do_rpc(query=b'foo') == [sha0]
    # with revision
    assert do_rpc(revision=b'branch/stable', query=b'add') == [sha2, sha0]
    # when revision does not exists
    assert do_rpc(revision=b'does_not_exists', query=b'add') == []
    # with no arg
    assert do_rpc() == []
    # with offset
    assert do_rpc(query=b'add', offset=1) == [sha0]
    # with limit
    assert do_rpc(query=b'add', limit=1) == [sha1]
    # with path
    assert do_rpc(query=b'add', path=b'foo') == [sha0]

    # on obsolete changeset
    wrapper.amend_file('animal')
    assert do_rpc(revision=sha2, query=b'add') == [sha2, sha0]


def test_find_all_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # prepare repo as:
    #
    #   o  3 (branch/stable)
    #   |
    #   | o  2 user: testuser2
    #   |/
    #   | 1 changes 'foo'
    #   |/
    #   o  0  creates 'foo'
    #

    def do_rpc(**opts):
        request = FindAllCommitsRequest(repository=grpc_repo, **opts)
        resp = grpc_stub.FindAllCommits(request)
        return [pycompat.sysbytes(commit.id)
                for chunk in resp for commit in chunk.commits]
    ctx0 = wrapper.commit_file('foo')
    timestamp = int(time.time())
    # commits with different date/time, to test with date ordering
    ctx1 = wrapper.commit_file('foo', parent=ctx0, utc_timestamp=timestamp+10)
    ctx2 = wrapper.commit_file('bar', parent=ctx0, user="testuser2",
                               utc_timestamp=timestamp+20)
    ctx3 = wrapper.commit_file('animals', branch='stable', parent=ctx0,
                               utc_timestamp=timestamp+15)
    sha0, sha1, sha2, sha3 = ctx0.hex(), ctx1.hex(), ctx2.hex(), ctx3.hex()

    # with revision
    assert do_rpc(revision=b'branch/stable') == [sha3, sha0]
    assert do_rpc(revision=b'branch/default') == [sha2, sha0]
    # when revision does not exists
    assert do_rpc(revision=b'does_not_exists') == []
    # with no arg, return all the commits
    assert do_rpc() == [sha3, sha2, sha1, sha0]
    # with skip
    assert do_rpc(skip=2) == [sha1, sha0]
    # with max_count
    assert do_rpc(max_count=2) == [sha3, sha2]
    # with date order (note that ctx2 date is latest than ctx3)
    assert do_rpc(order='DATE') == [sha2, sha3, sha1, sha0]
    # with topo order
    assert do_rpc(order='TOPO') == [sha3, sha2, sha1, sha0]
    # with obsolete revision (done at the end for no repercussions)
    wrapper.prune(sha3)
    assert ctx3.obsolete()
    assert do_rpc(revision=sha3) == [sha3, sha0]


def test_count_diverging_commits(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    def do_rpc(gl_from, gl_to, max_count=None):
        request = CountDivergingCommitsRequest(repository=grpc_repo,
                                               to=gl_to,
                                               max_count=max_count)
        setattr(request, 'from', gl_from)
        response = grpc_stub.CountDivergingCommits(request)
        return [response.left_count, response.right_count]

    # prepare repo as:
    #
    #   2 (branch/default)
    #   |
    #   1
    #   |  3 (topic/default/feature)
    #   | /
    #   0
    #
    ctx0 = wrapper.commit_file('foo')
    wrapper.commit_file('bar')
    wrapper.commit_file('baz')
    top_ctx = wrapper.commit_file('animals', topic='feature', parent=ctx0)

    assert do_rpc(b"branch/default", b"topic/default/feature") == [2, 1]
    # with commit given by full id
    assert do_rpc(b"branch/default", top_ctx.hex()) == [2, 1]
    # count 0 for the same "from" and "to"
    assert do_rpc(b"branch/default", b"branch/default") == [0, 0]
    # when one of them is invalid ref
    assert do_rpc(b"branch/default", b"does-not-exists") == [0, 0]
    assert do_rpc(b"does-not-exists", b"branch/default") == [0, 0]
    # count bounded with max_count
    for max_count in [1, 2, 3]:
        resp = do_rpc(b"branch/default", b"topic/default/feature", max_count)
        assert (resp[0] + resp[1]) == max_count
        resp = do_rpc(b"topic/default/feature", b"branch/default", max_count)
        assert (resp[0] + resp[1]) == max_count

    # with obsolete changeset
    wrapper.command('amend', message=b'amended')
    assert do_rpc(b"branch/default", top_ctx.hex()) == [2, 1]

    # with no ancestor
    wrapper.update('000000000000000000000000000')
    new_root = wrapper.commit_file('foo')
    assert do_rpc(top_ctx.hex(), new_root.hex()) == [2, 1]


def test_count_commits(commit_fixture_empty_repo):
    fixture = commit_fixture_empty_repo
    do_rpc = fixture.count_commits

    wrapper = fixture.repo_wrapper

    # prepare repo as:
    #
    #   2 (branch/default)
    #   |
    #   1
    #   |  3 (topic/default/feature)
    #   | /
    #   0
    #
    ctx0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('bar', parent=ctx0)
    wrapper.commit_file('baz', parent=ctx1)
    topic_hex = wrapper.commit_file('animals',
                                    topic='feature',
                                    parent=ctx0).hex()

    # simplest calls
    assert do_rpc(b'branch/default') == 3
    assert do_rpc(b'topic/default/feature') == 2
    assert do_rpc(topic_hex) == 2

    # when `all` is passed, return total commits in repo
    assert do_rpc(None, all=True) == 4
    assert do_rpc(None, max_count=2, all=True) == 2

    # range notation
    assert do_rpc(b'branch/default..topic/default/feature') == 1
    assert do_rpc(b'topic/default/feature..branch/default') == 2

    # cases of revision not found
    assert all(do_rpc(revision) == 0
               for revision in (b'branch/default..unknown',
                                b'unknown..topic/default/feature',
                                b'unknown'))

    # obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(topic_hex) == 2
    assert do_rpc(b'branch/default..' + topic_hex) == 1
    assert do_rpc(topic_hex + b'..branch/default') == 2

    # error cases
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(None)
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_get_commit_messages(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # prepare repo as:
    #
    #   1 (branch/default) changes 'foo'
    #   |
    #   0 creates 'foo'
    #
    ctx0 = wrapper.commit_file('foo', message=b'added foo')
    ctx1 = wrapper.commit_file('foo', message=b'changes foo')
    sha0, sha1 = ctx0.hex(), ctx1.hex()

    def do_rpc(commit_ids):
        request = GetCommitMessagesRequest(repository=grpc_repo,
                                           commit_ids=commit_ids)
        response = grpc_stub.GetCommitMessages(request)
        results = {}
        for resp in response:
            commit_id = resp.commit_id
            if commit_id:
                results[commit_id] = resp.message
        return list(results.values())
    assert do_rpc([sha1, sha0]) == [b"changes foo", b"added foo"]
    assert do_rpc([sha1]) == [b"changes foo"]

    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc([sha1, '12ca34de' * 5, sha0])
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'object not found' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx1.obsolete()
    assert do_rpc([sha1]) == [b"changes foo"]


def test_commit_stats(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    # repo structure:
    #
    #   2 Removed two lines
    #   |
    #   1 added one line, removed one
    #   |
    #   0 added foo
    #
    sha0 = wrapper.commit_file(
        'foo',
        content="First line\nSecond line\nThird line\n",
        message=b'added foo'
    ).hex()

    sha1 = wrapper.commit_file(
        'foo',
        content="Second line\nThird line\nFourth line\n",
        message=b'added one line, removed one'
    ).hex()

    ctx2 = wrapper.commit_file(
        'foo',
        content="Fourth line\n",
        message=b'Removed two lines'
    )
    sha2 = ctx2.hex()

    def do_rpc(rev):
        request = CommitStatsRequest(repository=grpc_repo,
                                     revision=rev)
        resp = grpc_stub.CommitStats(request)
        return resp.additions, resp.deletions

    assert do_rpc(sha0) == (3, 0)
    assert do_rpc(sha1) == (1, 1)
    assert do_rpc(sha2) == (0, 2)

    # with unknown revision
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(b"23fire32" * 5)
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'object not found' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert ctx2.obsolete()
    assert do_rpc(sha2) == (0, 2)


def test_raw_blame(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)
    # repo structure:
    #
    #   2 updated both lines
    #   |
    #   1 added one more line
    #   |
    #   0 added first line to foo
    #
    sha0 = wrapper.commit_file(
        'foo', message=b'zefoo',
        content='Second line\n'
                'Third line\n'
    ).hex()

    sha1 = wrapper.commit_file(
        'foo', message=b'zefoo',
        content='First line\n'
                'Second line\n'
                'Third line\n'
                'Forth line\n'
    ).hex()

    def do_rpc(rev, path, **kw):
        request = RawBlameRequest(repository=grpc_repo,
                                  revision=rev,
                                  path=path,
                                  **kw)
        response = grpc_stub.RawBlame(request)
        data = [resp.data for resp in response]
        return b''.join(data)

    assert do_rpc(sha0, b'foo') == (
        b'%s 1 1\n'
        b'\tSecond line\n'
        b'%s 2 2\n'
        b'\tThird line\n' % (sha0, sha0)
    )

    expected_rev1 = (
        b'%s 1 1\n'
        b'\tFirst line\n'
        b'%s 1 2\n'
        b'\tSecond line\n'
        b'%s 2 3\n'
        b'\tThird line\n'
        b'%s 4 4\n'
        b'\tForth line\n' % (sha1, sha0, sha0, sha1)
    )
    assert do_rpc(sha1, b'foo') == expected_rev1

    expected_rev1_range = (
        b'%s 1 1\n'
        b'\tSecond line\n'
        b'%s 2 2\n'
        b'\tThird line\n' % (sha0, sha0)
    )
    assert do_rpc(sha1, b'foo', range=b'2,3') == expected_rev1_range

    # with unknown revision
    assert do_rpc(b"23fire32" * 5, b'foo') == b''

    # with empty path
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha0, b'')
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'empty Path' in exc_info.value.details()

    # with unknown path
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha0, b'unknown')
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert 'not found in revision' in exc_info.value.details()

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(sha1, b'foo') == expected_rev1

    # bad range
    with pytest.raises(grpc.RpcError) as exc_info:
        do_rpc(sha1, b'foo', range=b'100,200')


def test_list_files(grpc_channel, server_repos_root):
    grpc_stub = CommitServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    sha0 = wrapper.commit_file('foo').hex()
    sha1 = wrapper.commit_file('bar').hex()
    sha2 = wrapper.commit_file('zoo').hex()

    def do_rpc(rev):
        request = ListFilesRequest(repository=grpc_repo,
                                   revision=rev)
        response = grpc_stub.ListFiles(request)
        final = []
        for resp in response:
            final.extend(resp.paths)
        return final

    assert do_rpc(sha0) == [b'foo']
    assert do_rpc(sha1) == [b'bar', b'foo']
    assert do_rpc(sha2) == [b'bar', b'foo', b'zoo']

    # with unknown revision
    assert do_rpc(b"23fire32" * 5) == []

    # special cases of invalid commit ids (prefix or full)
    assert do_rpc(b"f" * 39) == []
    assert do_rpc(b"f" * 40) == []

    # with obsolescence
    wrapper.command('amend', message=b'amended')
    assert do_rpc(sha2) == [b'bar', b'foo', b'zoo']


def test_list_commits(commit_fixture_empty_repo):
    fixture = commit_fixture_empty_repo
    wrapper = fixture.repo_wrapper
    list_commits = fixture.list_commits

    # see graph in Gitaly Comparison test
    ctx0 = wrapper.commit_file('foo', message="root changeset")
    sha0 = ctx0.hex()
    ctx1 = wrapper.commit_file('foo', topic='sampletop')
    sha1 = ctx1.hex()
    wrapper.update(ctx0.rev())
    wrapper.command(b'mv', wrapper.repo.root + b'/foo',
                    wrapper.repo.root + b'/zoo')
    ts = int(time.time() - 50)
    sha2 = wrapper.commit([b'foo', b'zoo'],
                          message=b"rename foo to zoo",
                          utc_timestamp=ts - 10,).hex()
    ctx3 = wrapper.commit_file('animals', branch='stable', parent=ctx0,
                               utc_timestamp=ts+10,
                               user='testuser <testuser@heptapod.test')
    sha3 = ctx3.hex()
    wrapper.update(2)
    ctx4 = wrapper.merge_commit(ctx3, message=b'merge with stable',
                                utc_timestamp=ts+20)

    sha4 = ctx4.hex()

    def caret(ctx):
        return b'^' + ctx.hex()

    assert list_commits('--visible') == [sha4, sha3, sha2, sha1, sha0]
    assert list_commits('--visible', caret(ctx3)) == [sha4, sha2, sha1]
    assert list_commits(sha4, caret(ctx1)) == [sha4, sha3, sha2]
    assert list_commits(sha4, caret(ctx1), reverse=True) == [sha2, sha3, sha4]
    assert list_commits(sha4, caret(ctx1), skip=1) == [sha3, sha2]

    # limit and cursor / page token
    assert fixture.list_commits_with_cursor(sha4, limit=2) == (
        [sha4, sha3], sha3
    )
    assert list_commits(sha4, limit=10, page_token=sha2) == [ctx0.hex()]

    # orderings
    Order = ListCommitsRequest.Order
    assert list_commits(sha4, order=Order.TOPO) == [sha4, sha3, sha2, sha0]
    # being the only one with no explicit date, ctx0 looks to be
    # the most recent one.
    assert list_commits(sha4, order=Order.DATE) == [sha0, sha4, sha3, sha2]

    # no result
    assert list_commits(sha4, caret(ctx4)) == []

    # disable walk
    assert list_commits(sha4, disable_walk=True) == [sha4]

    # message patterns
    assert list_commits(sha4, commit_message_patterns=[b'foo']) == [sha2]
    assert set(
        list_commits(sha4, commit_message_patterns=[b'foo', b'root'])
    ) == {sha0, sha2}
    assert list_commits(sha4,
                        commit_message_patterns=[b'FOO'],
                        ignore_case=True) == [sha2]

    # max_parents
    assert list_commits(sha4, max_parents=2) == list_commits(sha4)
    assert list_commits(sha4, max_parents=3) == list_commits(sha4)
    assert list_commits(sha4, max_parents=1) == [sha3, sha2, sha0]

    # dates
    date, date2 = Timestamp(), Timestamp()
    date.FromSeconds(ts+10)
    assert list_commits(sha4, before=date) == [sha3, sha2]
    assert list_commits(sha4, after=date) == [sha4, sha3, sha0]
    # gracinet: given that before is < and after is > I didn't expect
    # after=before to return anything, but `hg help dates` says that
    # the `to` range specifier is inclusive.
    assert list_commits(sha4, after=date, before=date) == [sha3]
    date2.FromSeconds(ts+40)
    assert list_commits(sha4, after=date, before=date2) == [sha4, sha3]

    # author regexp
    assert list_commits(sha4, author=b't.stuser') == [sha3]

    # paths
    assert list_commits(sha4, paths=[b'animals']) == [sha3]
    assert list_commits(sha4, paths=[b'anim*']) == [sha3]
    # Mercurial does not count the merge (see also comment in Comp test)
    assert list_commits(sha4,
                        paths=[b'foo', b'animals']) == [sha3, sha2, sha0]

    # unknown revision, including special cases:
    for unknown in ('branch/unknown',
                    'f' * 39,  # wdir node id, prefix
                    'f' * 40,  # wdir full node id
                    ):
        with pytest.raises(grpc.RpcError) as exc_info:
            list_commits(as_bytes(unknown))

        assert exc_info.value.code() == grpc.StatusCode.INTERNAL
        assert unknown in exc_info.value.details()

    # invalid arguments
    with pytest.raises(grpc.RpcError) as exc_info:
        list_commits()
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert 'revision' in exc_info.value.details()

    with pytest.raises(grpc.RpcError) as exc_info:
        list_commits(sha0, commit_message_patterns=[b'+'])
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL
    assert 'invalid regexp' in exc_info.value.details()

    # with obsolete changeset
    wrapper.command('amend', message=b'amended')
    assert ctx4.obsolete()
    assert list_commits(sha4, limit=2) == [sha4, sha3]
