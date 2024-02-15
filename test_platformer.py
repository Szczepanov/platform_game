from platformer import Player, Game, PowerUp, Coin, Platform
from unittest.mock import patch


def test_player_initialization():
    player = Player(100, 100, {'left': 'a', 'right': 'd', 'jump': 'w'}, (255, 0, 0))
    assert player.rect.x == 75
    assert player.rect.y == 75
    assert player.controls == {'left': 'a', 'right': 'd', 'jump': 'w'}
    assert player.original_color == (255, 0, 0)


def test_game_initialization():
    game = Game()
    assert game.players == []
    assert game.platforms == []
    assert game.coins == []
    assert game.power_ups == []


def test_powerup_initialization():
    powerup = PowerUp(100, 100, 'DoubleScore')
    assert powerup.rect.x == 90
    assert powerup.rect.y == 90
    assert powerup.type == 'DoubleScore'


def test_coin_initialization():
    coin = Coin(100, 100)
    assert coin.rect.x == 90
    assert coin.rect.y == 90


def test_platform_initialization():
    platform = Platform(100, 100, 200, 20)
    assert platform.rect.x == 100
    assert platform.rect.y == 100
    assert platform.rect.width == 200
    assert platform.rect.height == 20


def test_player_color_change_on_powerup():
    game = Game()
    player = Player(100, 100, {'left': 'a', 'right': 'd', 'jump': 'w'}, (255, 0, 0))
    game.players.append(player)
    powerup = PowerUp(100, 100, 'Invincibility')
    game.power_ups.append(powerup)
    game.update()
    assert player.image.get_at((0, 0)) == (255, 255, 255)  # Check if player color changed to white


def test_score_increase_on_coin_pickup():
    game = Game()
    player = Player(100, 100, {'left': 'a', 'right': 'd', 'jump': 'w'}, (255, 0, 0))
    game.players.append(player)
    coin = Coin(100, 100)
    game.coins.append(coin)
    initial_score = game.total_score
    game.update()
    assert game.total_score == initial_score + 1  # Check if score increased by 1




def test_player_color_reset_after_powerup_ends():
    with patch('time.time', return_value=0):  # Mock time.time() to always return 0
        game = Game()
        player = Player(100, 100, {'left': 'a', 'right': 'd', 'jump': 'w'}, (255, 0, 0))
        game.players.append(player)
        powerup = PowerUp(100, 100, 'Invincibility')
        game.power_ups.append(powerup)
        game.update()
        assert player.image.get_at((0, 0)) == (255, 255, 255)  # Check if player color changed to white

    with patch('time.time', return_value=11):  # Mock time.time() to return 11, simulating the passage of 11 seconds
        game.update()
        assert player.image.get_at((0, 0)) == (255, 0, 0)  # Check if player color reset to original color
