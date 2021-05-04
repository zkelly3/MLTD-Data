import axios from 'axios';

export class AjaxAPI {
    constructor() {
    }
    getIdols() {
        return axios.get(`/api/idols`);
    }
    getCards() {
        return axios.get(`/api/cards`);
    }
    getCardFilters() {
        return axios.get(`/api/cards/filters`);
    }
    getCardSorts() {
        return axios.get(`/api/cards/sorts`);
    }
    getCardIdols() {
        return axios.get(`/api/cards/idols`);
    }
    getEvents() {
        return axios.get(`/api/events`);
    }
    getEventTypes() {
        return axios.get(`/api/events/types`);
    }
    getGashas() {
        return axios.get(`/api/gashas`);
    }
    getGashaTypes() {
        return axios.get(`/api/gashas/types`);
    }
    getSongs() {
        return axios.get(`/api/songs`);
    }
    getIdol(idolId) {
        return axios.get(`/api/idol/${idolId}`);
    }
    getCard(cardId) {
        return axios.get(`/api/card/${cardId}`);
    }
    getCardTitle(cardId) {
        return axios.get(`/api/card/title/${cardId}`);
    }
    getEvent(eventType, eventId) {
        return axios.get(`/api/event/${eventType}/${eventId}`);
    }
    getGasha(gashaId) {
        return axios.get(`/api/gasha/${gashaId}`);
    }
}