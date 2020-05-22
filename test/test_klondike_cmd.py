from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, mock_open

from pytience.cards.deck import Suit
from pytience.cmd.klondike import KlondikeCmd, DEFAULT_SAVE_FILE
from pytience.games.solitaire.klondike import KlondikeGame

ORIGINAL_KLONDIKECMD_LOAD = KlondikeCmd.load


@patch('pytience.cmd.klondike.KlondikeCmd.load', side_effect=FileNotFoundError)
class KlondikeCmdTestCase(TestCase):
    def test_init(self, cmd_load):
        klondike = KlondikeCmd()
        self.assertEqual(len(klondike.errors), 0)
        cmd_load.assert_called_once()
        cmd_load.side_effect = Exception()
        klondike = KlondikeCmd()
        self.assertEqual(len(klondike.errors), 1)
        self.assertIsNotNone(klondike.klondike)

    @patch('pytience.cmd.klondike.KlondikeCmd.print_game')
    def test_preloop(self, cmd_print_game, _cmd_load):
        cmd_print_game.assert_not_called()
        KlondikeCmd().preloop()
        cmd_print_game.assert_called_once()

    @patch('cmd.Cmd.do_help')
    @patch('builtins.input', side_effect=EOFError)
    def test_do_help(self, _cmd_input, cmd_super_do_help, _cmd_load):
        klondike = KlondikeCmd()
        self.assertTrue(klondike.do_help('') is not True)
        cmd_super_do_help.assert_called_once()

    def test_do_quit(self, _cmd_load):
        klondike = KlondikeCmd()
        self.assertTrue(klondike.do_quit(''))

    def test_do_new(self, _cmd_load):
        klondike = KlondikeCmd()
        klondike.klondike = None
        self.assertIsNone(klondike.klondike)
        self.assertTrue(klondike.do_new('') is not True)
        self.assertIsNotNone(klondike.klondike)
        self.assertEqual(len(klondike.errors), 0)

    @patch('pytience.games.solitaire.klondike.KlondikeGame.undo')
    def test_do_undo(self, game_undo, _cmd_load):
        game_undo.assert_not_called()
        self.assertTrue(KlondikeCmd().do_undo('') is not True)
        game_undo.assert_called_once()

    @patch('pytience.games.solitaire.klondike.KlondikeGame.deal')
    def test_do_deal(self, game_deal, _cmd_load):
        game_deal.assert_not_called()
        self.assertTrue(KlondikeCmd().do_deal('') is not True)
        game_deal.assert_called_once()

    @patch('pytience.games.solitaire.klondike.KlondikeGame.select_waste')
    def test_do_waste(self, game_select_waste, _cmd_load):
        klondike = KlondikeCmd()
        self.assertTrue(klondike.do_waste('') is not True)
        game_select_waste.assert_called_with(None)
        self.assertTrue(klondike.do_waste('5') is not True)
        game_select_waste.assert_called_with(5)

    @patch('pytience.games.solitaire.klondike.KlondikeGame.select_foundation')
    def test_do_foundation(self, game_select_foundation, _cmd_load):
        klondike = KlondikeCmd()
        self.assertEqual(len(klondike.errors), 0)
        self.assertTrue(klondike.do_foundation('') is not True)
        self.assertEqual(len(klondike.errors), 1)
        game_select_foundation.assert_not_called()

        klondike = KlondikeCmd()
        self.assertEqual(len(klondike.errors), 0)
        self.assertTrue(klondike.do_foundation('foobar') is not True)
        self.assertEqual(len(klondike.errors), 1)
        game_select_foundation.assert_not_called()

        self.assertTrue(klondike.do_foundation('c') is not True)
        game_select_foundation.assert_called_with(Suit.Clubs, None)

        self.assertTrue(klondike.do_foundation('h 1') is not True)
        game_select_foundation.assert_called_with(Suit.Hearts, 1)

    @patch('pytience.games.solitaire.klondike.KlondikeGame.select_tableau')
    def test_do_tableau(self, game_select_tableau, _cmd_load):
        klondike = KlondikeCmd()
        self.assertEqual(len(klondike.errors), 0)
        self.assertTrue(klondike.do_tableau('') is not True)
        self.assertEqual(len(klondike.errors), 1)
        game_select_tableau.assert_not_called()

        klondike = KlondikeCmd()
        self.assertTrue(klondike.do_tableau('0') is not True)
        game_select_tableau.assert_called_with(0, -1, None)

        self.assertTrue(klondike.do_tableau('0 0') is not True)
        game_select_tableau.assert_called_with(0, 0, None)

        self.assertTrue(klondike.do_tableau('0 0 1') is not True)
        game_select_tableau.assert_called_with(0, 0, 1)

    @patch('pytience.games.solitaire.klondike.KlondikeGame.solve')
    def test_do_solve(self, game_solve, _cmd_load):
        game_solve.assert_not_called()
        self.assertTrue(KlondikeCmd().do_solve('') is not True)
        game_solve.assert_called_once()

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save(self, path_mkdir, _mock_open, _json_dump, _cmd_load):
        klondike = KlondikeCmd()
        self.assertTrue(KlondikeCmd.save(klondike.klondike, 'resources/foobar.json') is not True)
        path_mkdir.assert_called_once()
        _mock_open.assert_called_with(Path('resources/foobar.json'), 'w')

    @patch('pytience.cmd.klondike.KlondikeCmd.save')
    def test_do_save(self, cmd_save, _cmd_load):
        klondike = KlondikeCmd()
        cmd_save.assert_not_called()
        self.assertTrue(klondike.do_save('') is not True)
        cmd_save.assert_called_with(klondike.klondike, DEFAULT_SAVE_FILE)
        self.assertTrue(klondike.do_save('resources/foobar.json') is not True)
        cmd_save.assert_called_with(klondike.klondike, 'resources/foobar.json')

    @patch('json.load', side_effect=dict)
    @patch('builtins.open', new_callable=mock_open)
    def test_load(self, _mock_open, _json_load, _cmd_load):
        klondike = ORIGINAL_KLONDIKECMD_LOAD('resources/foobar.json')
        self.assertIsInstance(klondike, KlondikeGame)

    def test_do_load(self, _cmd_load):
        klondike = KlondikeCmd()
        self.assertTrue(klondike.do_load('') is not True)
        _cmd_load.assert_called_with(DEFAULT_SAVE_FILE)
        self.assertTrue(klondike.do_load('resources/foobar.json') is not True)
        _cmd_load.assert_called_with('resources/foobar.json')

    @patch('pytience.cmd.klondike.KlondikeCmd.print_game')
    @patch('pytience.cmd.klondike.KlondikeCmd.save')
    def test_postcmd(self, cmd_save, cmd_print_game, _cmd_load):
        klondike = KlondikeCmd()
        cmd_save.assert_not_called()
        cmd_print_game.assert_not_called()
        self.assertTrue(klondike.postcmd(False, None) is False)
        cmd_save.assert_called_once()
        cmd_print_game.assert_called_once()
        self.assertTrue(klondike.postcmd(True, None) is True)

    @patch('pytience.cmd.klondike.KlondikeCmd.do_tableau')
    @patch('pytience.cmd.klondike.KlondikeCmd.print_dump')
    @patch('builtins.input', side_effect=EOFError)
    def test_default(self, _mock_input, cmd_print_dump, cmd_do_tableau, _cmd_load):
        klondike = KlondikeCmd()
        cmd_print_dump.assert_not_called()
        self.assertTrue(klondike.default('_dump') is not True)
        cmd_print_dump.assert_called_once()

        cmd_do_tableau.assert_not_called()
        self.assertTrue(klondike.default('1') is not True)
        cmd_do_tableau.assert_called_with('1')

        self.assertTrue(klondike.default('1 2') is not True)
        cmd_do_tableau.assert_called_with('1 2')

        self.assertTrue(klondike.default('1 2 3') is not True)
        cmd_do_tableau.assert_called_with('1 2 3')

        self.assertTrue(klondike.default('t 4 5 6') is not True)
        cmd_do_tableau.assert_called_with('4 5 6')

        self.assertEqual(len(klondike.errors), 0)
        self.assertTrue(klondike.default('foo bar') is not True)
        self.assertEqual(len(klondike.errors), 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_dump(self, sys_stdout, _cmd_load):
        klondike = KlondikeCmd()
        self.assertEqual(sys_stdout.getvalue(), '')
        klondike.print_dump()
        self.assertNotEqual(sys_stdout.getvalue(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_game(self, sys_stdout, _cmd_load):
        klondike = KlondikeCmd()
        self.assertEqual(sys_stdout.getvalue(), '')
        klondike.print_game()
        self.assertNotEqual(sys_stdout.getvalue(), '')
