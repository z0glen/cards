from flask import jsonify, request
from flask_socketio import join_room, emit
from flask_cors import cross_origin
import sys

from app import app, socketIO
from app.helpers import read_file
from app.helpers import load_from_file
from app.game import Game
from app.player import Player
from app.models import CallCard, ResponseCard

# dict for tracking active games
# game code to game object
ROOMS = {}
# dict for tracking active users
# sid to player object
USERS = {}

def bulk_update_user_data(users):
    for u in users:
        emit('user_data', u.to_json(), room=u.sid)

def is_new_sid(sid):
    if USERS[sid]:
        return False
    return True

@app.route('/importcards')
@cross_origin()
def import_cards():
    app.logger.info("Importing cards from file!")
    return jsonify(load_from_file())

@app.route('/decks')
@cross_origin()
def get_cards():
    decks = {
        'Core': {
            'calls': CallCard.query.all(),
            'responses': ResponseCard.query.all()
        }
    }
    return jsonify(decks)

@socketIO.on('create')
def on_create(data):
    """Create a game lobby"""
    app.logger.info("Creating a new game!")
    curr_game = Game()
    # TODO: check for duplicate names
    player = Player(data['name'], curr_game, request.sid)
    curr_game.players[data['name']] = player
    ROOMS[curr_game.id] = curr_game
    USERS[player.sid] = player
    join_room(curr_game.id)
    emit('set_username', data['name'])
    emit('user_data', player.to_json())
    emit('join_room', {'room': curr_game.to_json()})

@socketIO.on('join')
def on_join(data):
    """Join a game lobby"""
    app.logger.info("Joining game! code: " + data['room'])
    room = data['room'].upper()
    if room in ROOMS and ROOMS[room].is_valid_username(data['name']):
        join_room(room)
        player = Player(data['name'], ROOMS[room], request.sid)
        ROOMS[room].add_player(player)
        USERS[player.sid] = player
        emit('set_username', data['name'])
        emit('user_data', player.to_json())
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)
    elif room in ROOMS:
        emit('error', {'error': "That username is already taken!", 'errorField': "username"})
    else:
        emit('error', {'error': "Game not found :(", 'errorField': "code"})

@socketIO.on('connect')
def on_connect():
    """When a new user connects"""
    global USERS
    app.logger.info("User joined! " + request.sid)
    USERS[request.sid] = {}

@socketIO.on('disconnect')
def on_disconnect():
    """When a user closes the window"""
    # TODO check if user in game and remove
    global USERS
    app.logger.info("User exited " + request.sid)
    if USERS[request.sid]:
        curr_game = USERS[request.sid].game
        curr_game.remove_player(request.sid)
        if len(curr_game.players) == 1 and curr_game.state != "lobby":
            curr_game.state = "lobby"
            emit('error', {'error': "All other players have exited! Returning to the lobby."}, room=curr_game.id)
        if curr_game.state == "active" and curr_game.has_all_played():
            curr_game.state = "judging"
        emit('played_cards', list(curr_game.played_cards.values()), room=curr_game.id)
        emit('join_room', {'room': curr_game.to_json()}, room=curr_game.id)
    del USERS[request.sid]

@socketIO.on('pingServer')
def pingServer(data):
    """Test websocket connection"""
    app.logger.debug(data)

@socketIO.on('setState')
def setState(data):
    """Set the game state"""
    app.logger.debug(data)
    room = data['room']
    if room in ROOMS and data['state'] == 'active':
        ROOMS[room].state = data['state']
        ROOMS[room].reset_round()
        bulk_update_user_data(ROOMS[room].players.values())
        # TODO: rename channel to reflect that it also updates
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)

@socketIO.on('playCard')
def playCard(data):
    """When a player selects a card for judging"""
    app.logger.info("playCard event received: " + str(data))
    room = data['room']
    if room in ROOMS:
        player = USERS[request.sid]
        player.play_card(data['card'])
        if ROOMS[room].has_all_played():
            ROOMS[room].state = "judging"
            ROOMS[room].shuffle_played_cards()
        emit('user_data', player.to_json())
        emit('played_cards', ROOMS[room].played_cards, room=room)
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)
    else:
        app.logger.warning("invalid room: " + room)
        app.logger.debug("available rooms")
        app.logger.debug(str(ROOMS))
        emit('error', {"error": "This game room no longer exists. Please make a new one."})

@socketIO.on('judgeCard')
def judgeCard(data):
    """When the judge chooses a card to win the round"""
    app.logger.debug("judgeCard event received")
    room = data['room']
    if room in ROOMS:
        win_data = ROOMS[room].award_point(data['card'])
        ROOMS[room].state = "roundOver"
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)
        emit('round_over', win_data, room=room)

@socketIO.on('newRound')
def newRound(data):
    """A request for fresh data when starting a new round"""
    room = data['room']
    if room in ROOMS and ROOMS[room].state != "active":
        ROOMS[room].state = "active"
        ROOMS[room].end_round()
        bulk_update_user_data(ROOMS[room].players.values())
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)
    elif room in ROOMS:
        app.logger.debug("Cannot request new round while game is active.")

@socketIO.on('joinRoom')
def joinRoom(data):
    """On refresh, need to re-join the socket io room"""
    room = data['room']
    app.logger.info("sid " + request.sid + " is joining room " + room)
    if room in ROOMS and is_new_sid(request.sid):
        join_room(room)
        player = Player(data['userData']['name'], ROOMS[room], request.sid)
        ROOMS[room].add_player(player)
        USERS[player.sid] = player
        emit('set_username', data['userData']['name'])
        emit('user_data', player.to_json())
        emit('join_room', {'room': ROOMS[room].to_json()}, room=room)
