import pytest
import unittest
from platformer import Player, Coin, Platform, PowerUp, Game, DoubleScore, SCREEN_WIDTH, SCREEN_HEIGHT


class TestPlayer(unittest.TestCase):
    @pytest.fixture
    def player(self):
        return Player(400, 300, {'left': 0, 'right': 0, 'up': 0}, (255, 0, 0))

    def test_initialization2(self, player):
        assert player.rect.x == 400
        assert player.rect.y == 300
        assert player.image.fill() == (255, 0, 0)

    def setUp(self):
        self.player = Player(400, 300, {'left': 0, 'right': 0, 'up': 0}, (255, 0, 0))

    def test_initialization(self):
        self.assertEqual(self.player.rect.x, 400)
        self.assertEqual(self.player.rect.y, 300)
        self.assertEqual(self.player.image.fill(), (255, 0, 0))

    # Add more tests for Player methods


class TestCoin(unittest.TestCase):
    def setUp(self):
        self.coin = Coin(100, 100)

    def test_initialization(self):
        self.assertEqual(self.coin.rect.x, 100)
        self.assertEqual(self.coin.rect.y, 100)
        self.assertEqual(self.coin.image.fill(), (255, 255, 0))

    # Add more tests for Coin methods


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_update_level(self):
        self.game.update_level(50)
        self.assertEqual(self.game.level, 3)

    def test_reset_game(self):
        players = [Player(400, 300, {'left': 0, 'right': 0, 'up': 0}, (255, 0, 0)) for _ in range(2)]
        coins = [Coin(100, 100) for _ in range(5)]
        power_ups = [PowerUp(200, 200, DoubleScore()) for _ in range(2)]
        platforms = []
        self.game.reset_game(players, coins, power_ups, platforms)
        self.assertEqual(self.game.power_up, None)
        self.assertEqual(self.game.power_up_start_time, None)
        self.assertEqual(len(coins), 0)
        self.assertEqual(len(power_ups), 0)
        for player in players:
            self.assertEqual(player.rect.x, SCREEN_WIDTH // 2)
            self.assertEqual(player.rect.y, SCREEN_HEIGHT // 2)
            self.assertEqual(player.vel_y, 0)
            self.assertEqual(player.jumps, 0)
            self.assertEqual(player.score, 0)


class TestPowerUp(unittest.TestCase):
    def setUp(self):
        self.power_up = PowerUp(200, 200, DoubleScore())

    def test_initialization(self):
        self.assertEqual(self.power_up.rect.x, 200)
        self.assertEqual(self.power_up.rect.y, 200)
        self.assertIsInstance(self.power_up.type, DoubleScore)

    def test_effect(self):
        player = Player(400, 300, {'left': 0, 'right': 0, 'up': 0}, (255, 0, 0))
        player.score = 10
        self.power_up.type.apply(player)
        self.assertEqual(player.score, 20)


class TestPlatform(unittest.TestCase):
    def setUp(self):
        self.platform = Platform(100, 200, 50, 10)

    def test_initialization(self):
        self.assertEqual(self.platform.rect.x, 100)
        self.assertEqual(self.platform.rect.y, 200)
        self.assertEqual(self.platform.rect.width, 50)
        self.assertEqual(self.platform.rect.height, 10)

