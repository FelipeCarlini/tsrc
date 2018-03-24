def test_happy(tsrc_cli, git_server, message_recorder):
    git_server.add_repo("foo")
    git_server.add_repo("spam")
    git_server.push_file("foo", "bar.txt", message="boring bar")
    git_server.tag("foo", "v0.1")
    git_server.tag("spam", "v0.1")
    manifest_url = git_server.manifest_url
    tsrc_cli.run("init", manifest_url)
    git_server.push_file("foo", "foo.txt", message="new foo!")
    tsrc_cli.run("sync")
    message_recorder.reset()

    tsrc_cli.run("log", "--from", "v0.1")

    assert message_recorder.find("new foo!")

    message_recorder.reset()
    tsrc_cli.run("log", "--from", "v0.1", "--to", "v0.1")
    assert not message_recorder.find("new foo!")


def test_error(tsrc_cli, git_server):
    git_server.add_repo("foo")
    manifest_url = git_server.manifest_url
    tsrc_cli.run("init", manifest_url)

    tsrc_cli.run("log", "--from", "v0.1", expect_fail=True)
