/* ----- SCRIPTS GLOBALES ----- */

"use strict";

const days = [
    'Domingo',
    'Lunes',
    'Martes',
    'Miercoles',
    'Jueves',
    'Viernes',
    'Sabado'
]

const months = [
    'Enero',
    'Febrero',
    'Marzo',
    'Abril',
    'Mayo',
    'Junio',
    'Julio',
    'Agosto',
    'Septiembre',
    'Octubre',
    'Noviembre',
    'Deciembre'
]

//Se setea la fecha actual
let today = new Date();
let currentDay = days[today.getDay()];
let currentMonth = months[today.getMonth()];
document.getElementById("dateAndTime").innerHTML = `${currentDay} ${today.getDate()} de ${currentMonth} del ${today.getFullYear()}`;