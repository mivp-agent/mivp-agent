from mivp_agent.util.log_presenter import LogPresenter


def test_single(capsys):
    p = LogPresenter()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    with p:
        p.add('Source 1', 'Hello World\n My friend.')
        captured = capsys.readouterr()
        header = 'Source 1 | '
        header_idx = captured.out.find(header)

        line1 = 'Hello World'
        line1_idx = captured.out.find(line1)

        assert header_idx != -1
        assert line1_idx != -1
        # Header appears before text
        assert header_idx < line1_idx

        line2 = " My friend"
        assert captured.out.find(line2) == -1

    # After context is exited, cache should be dumped
    captured = capsys.readouterr()
    line2_idx = captured.out.find(line2)
    assert line2_idx != -1


def test_series(capsys):
    adds = (
        ('Source 1', 'Hello World\n My friend.'),
        ('Source 2', 'Hello Web\n'),
        ('Source 1', '\nBlah blah\n'),
        ('Source 2', 'Blee blah\n')
    )

    expected_order = (
        ('Source 1', ('Hello World\n',)),
        ('Source 2', ('Hello Web\n',)),
        ('Source 1', (' My friend.\n', 'Blah blah\n')),
        ('Source 2', ('Blee blah\n',))
    )

    # Dump all
    with LogPresenter() as p:
        for source, text in adds:
            p.add(source, text)

        captured = capsys.readouterr()
        out = captured.out
        for source, print_list in expected_order:
            for p in print_list:
                header_idx = out.find(source)
                print_idx = out.find(p)

                assert header_idx != -1 and print_idx != -1
                assert header_idx < print_idx

                # Split the captured output on print to remove it and everything before it.
                new_out = out.split(p)
                new_out = p.join(new_out[:3]) # [:3] will give anything in the 3rd index and past (anything after the first print)

                out = new_out
