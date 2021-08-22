<template>
    <div>
        <div class="container text-center">
            <b-jumbotron bg-variant="secondary" text-variant="white" header="Cards Against Online Player">
                <b-button v-b-modal.create-modal variant="primary" class="button">Create Game</b-button>
                <b-button v-b-modal.join-modal variant="success" class="button">Join Game</b-button>
                <b-button to="decks" variant="info" class="button">Manage Decks</b-button>
            </b-jumbotron>
            <b-jumbotron header="Gameplay Notes">
                <ul class="gameplay-notes">
                    <li>Use the buttons above to create a new game or join an existing game</li>
                    <li>Usernames need to be unique in each game</li>
                    <li>Players can join at any time during a game</li>
                    <li>Once you play a card, you cannot change it</li>
                    <li>For multi-card responses, play the cards in the order of the blanks</li>
                    <li>Currently players cannot leave mid-game, you will need to start a new game</li>
                    <li>This is an early access game that is actively under development - everything is subject to change</li>
                    <li>Please use the linked GitHub for bug reports and feature requests</li>
                </ul>
            </b-jumbotron>
        </div>
        <b-modal id="create-modal" hide-footer title="Create Game">
            <b-form @submit="createGame">
                <b-form-group
                    id="createName"
                    label="Name:"
                    label-for="name-input"
                    description="How you'll appear to other players."
                >
                    <b-form-input
                        id="name-input"
                        v-model="createForm.name"
                        required
                        placeholder="Enter name"
                    ></b-form-input>
                </b-form-group>
                <b-button type="submit" variant="primary">Submit</b-button>
            </b-form>
        </b-modal>
        <b-modal id="join-modal" hide-footer title="Join Game">
            <b-form @submit="joinGame">
                <b-form-group
                    id="joinName"
                    label="Name:"
                    label-for="name-input"
                    description="How you'll appear to other players."
                    :invalid-feedback="usernameInvalid"
                    :state="usernameState"
                >
                    <b-form-input
                        id="name-input"
                        v-model="joinForm.name"
                        required
                        placeholder="Enter name"
                        :state="usernameState"
                    ></b-form-input>
                </b-form-group>
                <b-form-group
                    id="joinRoom"
                    label="Game Code:"
                    label-for="code-input"
                    description="Your unique game code"
                    :invalid-feedback="gameCodeInvalid"
                    :state="gameCodeState"
                >
                    <b-form-input
                        id="code-input"
                        v-model="joinForm.room"
                        required
                        placeholder="Enter code"
                        :state="gameCodeState"
                    ></b-form-input>
                </b-form-group>
                <b-button type="submit" variant="primary">Submit</b-button>
            </b-form>
        </b-modal>
    </div>
</template>

<script>
    import { mapState } from 'vuex';

    export default {
        data() {
            return {
                createForm: {
                    name: "",
                },
                joinForm: {
                    name: "",
                    room: ""
                }
            };
        },
        computed: {
            usernameState() {
                return (this.error && this.errorField === 'username') ? false : null;
            },
            usernameInvalid() {
                if (this.error && this.errorField === 'username') {
                    return this.error;
                } else {
                    return "";
                }
            },
            gameCodeState() {
                return (this.error && this.errorField === 'code') ? false : null;
            },
            gameCodeInvalid() {
                if (this.error && this.errorField === 'code') {
                    return this.error;
                } else {
                    return "";
                }
            },
            ...mapState(['room', 'error', 'errorField']),
        },
        watch: {
            room(newState) {
                this.$router.push({name: 'Game', params: {code: newState.id}});
            }
        },
        methods: {
            createGame(evt) {
                evt.preventDefault();
                this.$store.commit('set_username', this.createForm.name);
                this.$socket.emit('create', this.createForm);
                //this.$router.push({name: 'Game', params: {code: this.createForm.room}});
            },
            joinGame(evt) {
                evt.preventDefault();
                this.$store.commit('set_username', this.joinForm.name);
                this.$socket.emit('join', this.joinForm);
                //this.$router.push({name: 'Game', params: {code: this.joinForm.room}});
            }
        },
        created() {
            this.$store.commit('error', {'error': '', 'errorField': ''});
        }
    }
</script>

<style scoped>
    .button {
        margin: 10px;
    }
    .gameplay-notes {
      list-style: inside;
    }
</style>