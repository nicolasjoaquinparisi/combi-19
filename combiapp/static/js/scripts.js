/* ----- LOGIN ----- */
function onRegisterButtonClick()
{
    let checkbox = document.getElementById("gold-member-container");
    document.getElementById("login-section").style.display    = "none";
    document.getElementById("register-section").style.display = "block";

    if (checkBox != null)
    {
        checkbox.style.display = "none";
    }
}


/* ----- ALTA DE USUARIO ----- */

//Función para mostrar / ocultar la información a cargar de la tarjeta para usuarios Gold
function onCheckBoxClick()
{
    let checkBox = document.getElementById("checkBox-goldMember");
    let goldMemberContainer = document.getElementById("gold-member-container")

    if (checkBox != null && goldMemberContainer != null)
    {
        if (checkBox.checked)
        {
            checkBox.value = "True"
            goldMemberContainer.style.display = "block";
            return;
        }

        checkBox.value = "False"
        goldMemberContainer.style.display = "none";
    }
}

//Validación para el alta de los usuarios (Se valida que todos los campos estén completos, como también, parte de la información ingresada)
(function () {
    let forms = document.querySelectorAll('.validacion-alta-usuario');
    Array.prototype.slice.call(forms)
    .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated')
            }, false)
        })
})()

/* ----- FIN ALTA DE USUARIO ----- */





/* ----- VALIDACION DE CONTRASEÑAS ------ */

let inputPassword = document.getElementById("password");
let length = document.getElementById("length");
let specialCharacter = document.getElementById("special-char");

let specialChars = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~";

if (inputPassword != null)
{
    inputPassword.onfocus = function () {
        document.getElementById("message").style.display = "block";
    }
    inputPassword.onblur = function () {
        document.getElementById("message").style.display = "none";
    }

    //Verificación de coincidencia de contraseñas
    let inputPasswordConfirm = document.getElementById("password_confirm");

    let passwordMatch = document.getElementById("password-match");
    let passwordDismatch = document.getElementById("password-dismatch");
    let passwordConfirmMatch = document.getElementById("password-confirm-match");
    let passwordConfirmDismatch = document.getElementById("password-confirm-dismatch");


    inputPassword.onkeyup = function () {

        // Validación del tamaño de la contraseña
        if (inputPassword.value.length >= 6) {
            length.classList.remove("invalid");
            length.classList.add("valid");
        } else {
            length.classList.remove("valid");
            length.classList.add("invalid");
        }

        // Validación del caracter especial
        specialCharacter.classList.remove("valid");
        specialCharacter.classList.add("invalid");

        for (let i = 0; i < inputPassword.value.length; i++) {
            for (let j = 0; j < specialChars.length; j++) {
                if (inputPassword.value[i] == specialChars[j]) {
                    specialCharacter.classList.remove("invalid");
                    specialCharacter.classList.add("valid");
                }
            }
        }
        if (inputPasswordConfirm != null)
            VerifyPasswords();
    }

    if (inputPasswordConfirm != null)
    {
        inputPasswordConfirm.onkeyup = function () {
            VerifyPasswords();
        }
    }

}

function VerifyPasswords()
{
    if (inputPassword.value == inputPasswordConfirm.value) {
        passwordDismatch.style.display = "none";
        passwordConfirmDismatch.style.display = "none";

        passwordConfirmMatch.style.display = "block";
        passwordMatch.style.display = "block";
    }
    else {
        passwordMatch.style.display = "none";
        passwordConfirmMatch.style.display = "none";

        passwordDismatch.style.display = "block";
        passwordConfirmDismatch.style.display = "block";
    }

    if ((inputPassword.value == "" & inputPasswordConfirm.value != "") | (inputPassword.value == "" & inputPasswordConfirm.value == "")) {
        passwordMatch.style.display = "none";
        passwordConfirmMatch.style.display = "none";
        passwordDismatch.style.display = "none";
        passwordConfirmDismatch.style.display = "none";
    }
}

/* ----- FIN VALIDACION DE CONTRASEÑAS ------ */
function isDateBeforeToday(date) {
    let today =  new Date(new Date().toDateString());
    let datePicked = new Date(date.toDateString());
    return datePicked.getMilliseconds() < today.getMilliseconds();
}

function buscarPasaje()
{
    let origen = document.querySelector("#origen").value
    let destino = document.querySelector("#destino").value
    let date = document.querySelector("#date").value

    if (origen <= 0)
    {
      showNotification('Error', 'Se debe seleccionar un origen.')
      return
    }

    if (destino <= 0)
    {
      showNotification('Error', 'Se debe seleccionar un destino.')
      return
    }

    if (origen == destino)
    {
        showNotification('Error', 'El origen y el destino no pueden ser iguales.')
        return
    }

    if (date == '')
    {
      showNotification('Error', 'Se debe seleccionar una fecha.')
      return
    }

    let day = parseInt(date[8] + date[9])
    let month = parseInt(date[5] + date[6])
    let year = parseInt(date[0] + date[1] + date[2] + date[3])

    if (isDateBeforeToday(new Date(year, month, day)))
    {
        showNotification('Error', 'La fecha ingresada es inválida')
        return
    }

    window.location.href = `/buscar-viajes/${origen}/${destino}/${date}`
}

function initialize()
{
    let buttonEnviar = document.getElementById('button-enviar');

    if (buttonEnviar != null)
    {
        buttonEnviar.disabled = true;
    }
}

/* ----- NUEVO COMENTARIO ----- */
function onInput(e)
{
    var commentSizeText  = document.getElementById('comment-size').innerHTML = e.target.value.length + "/280";
    var buttonEnviar     = document.getElementById('button-enviar');

    if (e.target.value.length == 0)
    {
        buttonEnviar.disabled = true;
        buttonEnviar.enabled = false;
    }
    else
    {
        buttonEnviar.enabled = true;
        buttonEnviar.disabled = false;
    }
}

/* --------------- COMPRAR PASAJE --------------- */
function recalcularPrecios()
{
    let precioPasajeSpan = document.querySelector("#precio_pasaje")
    let precioInsumosSpan = document.querySelector("#precio_insumos")
    let precioTotalSpan = document.querySelector("#precio_total")
    let precioDescuentoSpan = document.querySelector("#precio_descuento")
    let cantInsumo = document.querySelectorAll("[id^='cant_insumo_']")
    let precioInsumo = document.querySelectorAll("[id^='precio_insumo_']")

    let precioInsumos = 0.0
    for (let i = 0; i < Math.min(cantInsumo.length, precioInsumo.length); i++)
        precioInsumos += parseFloat(cantInsumo[i].innerHTML) * parseFloat(precioInsumo[i].innerHTML)

    precioInsumosSpan.innerHTML = precioInsumos

    let precioTotal = parseFloat(precioPasajeSpan.innerHTML) + precioInsumos
    precioTotalSpan.innerHTML = precioTotal
    if (precioDescuentoSpan !== null)
        precioDescuentoSpan.innerHTML = precioTotal * 0.9
}

function agregarInsumo(insumo_pk)
{
    let elem = document.querySelector("#cant_insumo_" + insumo_pk)
    let cant = parseInt(elem.innerHTML)
    elem.innerHTML = cant + 1
    recalcularPrecios()
}

function quitarInsumo(insumo_pk)
{
    let elem = document.querySelector("#cant_insumo_" + insumo_pk)
    let cant = parseInt(elem.innerHTML)
    if (cant <= 0)
        elem.innerHTML = 0
    else
        elem.innerHTML = cant - 1
    recalcularPrecios()
}

function comprarPasaje()
{
    let cantInsumosSpans = document.querySelectorAll("[id^='cant_insumo_']")
    for (let i = 0; i < cantInsumosSpans.length; i++)
    {
        let span = cantInsumosSpans[i]
        let cant = parseInt(span.innerHTML)
        let pk = span.getAttribute("pk")
        let cantInput = document.getElementById(`input_cant_insumo_${pk}`)
        cantInput.value = cant
    }

    let req = new XMLHttpRequest();
    req.onload = function() {
        if (req.status === 200)
        {
            let response = JSON.parse(req.responseText);
            showNotification(response.result, response.message);

            $("#success-button").click(function () {
                window.location.href = '/'
            });
        }
        else
        {
            let response = {
                "result": "Error",
                "message": "Error en la conexión con el servidor."
            };
            showNotification(response.result, response.message);
        }
    }
    req.onerror = function() {
        let response = {
            "result": "Error",
            "message": "Error en la conexión con el servidor."
        };
        showNotification(response.result, response.message);
    }

    req.open("post", "#");
    req.send(new FormData(document.getElementById("comprar_form")));
}

//  ----- LISTAR VIAJES -----

function setColorAsientos(asiento, cantidadDeAsientos)
{
    if (cantidadDeAsientos <= 5)
    {
        asiento.classList.add("text-danger")
    }
    else
    {
        asiento.classList.add("text-success")
    }
}

function setEstadoColor(estado)
{
    switch (estado.innerHTML)
    {
        case "Cancelado":
        case "Rechazado":
            estado.classList.add("text-danger");
            break;
        case "Iniciado":
            estado.classList.add("text-success");
            break;
        case "Pendiente":
            estado.style.color = "orange";
            break;
    }
}

//Función para poner en verde el color de la cantidad de pasajes disponibles cuando es mayor a 5, y en rojo cuando es menor
function onListarViajes()
{
    let asientosDisponbiles = document.getElementsByClassName("asientos-disponibles");
    let estados = document.getElementsByClassName("estado-pasaje");

    for (asiento of asientosDisponbiles)
    {
        let cantidadDeAsientos =  parseInt(asiento.innerHTML);
        setColorAsientos(asiento,cantidadDeAsientos);
    }

    for (estado of estados)
        setEstadoColor(estado);
}


// ----- VER PASAJE -----
function onVerPasaje()
{
    let totalInsumos         = document.getElementById("total-insumos-comestibles");
    let pasaje               = document.getElementById("precio-pasaje");
    let descuentoUsuarioGold = document.getElementById("descuento-usuario-gold");

    let precioInsumos = 0;
    if (totalInsumos != null)
    {
        precioInsumos = "";
        for (let i = 1; i < totalInsumos.innerHTML.length; i++)
            precioInsumos += totalInsumos.innerHTML[i];
        precioInsumos = parseFloat(precioInsumos);
    }


    let precioPasaje = "";
    for (let i = 1; i < pasaje.innerHTML.length; i++)
        precioPasaje += pasaje.innerHTML[i];
    precioPasaje = parseFloat(precioPasaje);

    let descuento = ((precioPasaje + precioInsumos) * 10) / 100;

    descuentoUsuarioGold.innerHTML = "$" + descuento;
}

function setEstadoPasajeColor()
{
    let estado = document.getElementById("estado-pasaje");

    switch (estado.innerHTML)
    {
        case "Cancelado":
            estado.classList.add("text-danger");
            break;
        case "Iniciado":
            estado.classList.add("text-success");
            break;
        case "Pendiente":
            estado.style.color = "orange";
            break;
    }
}

function initializeVerPasaje()
{
    setEstadoPasajeColor();
    onVerPasaje();
}

// ----- MIS VIAJES -----
function initializeMisViajes()
{
    let estados = document.getElementsByClassName("estado-pasaje");

    for (let i = 0; i < estados.length; i++)
    {
        if (estados != null)
        {
            let estado = estados[i];
            setEstadoColor(estado);
        }
    }
}


// ------- EDITAR COMENTARIO -------------
function initializeMisComentarios()
{
    let inputs = document.getElementsByClassName("input-area");
    let buttons = document.getElementsByClassName("edit-buttons");

    let options = document.getElementsByClassName("options");
    let texts = document.getElementsByClassName("comentario-texto");

    for (option of options)
        option.style.display = "block";

    for (text of texts)
        text.style.display = "block";

    for (let input of inputs)
        input.style.display = "none";

    for (let button of buttons)
        button.style.display = "none";
}

function onEditButtonClick(index)
{
    initializeMisComentarios();

    let inputs = document.getElementsByClassName("input-area");
    let buttons = document.getElementsByClassName("edit-buttons");  //Botones Editar y Cancelar

    let options = document.getElementsByClassName("options");       //Editar y Borrar
    let texts = document.getElementsByClassName("comentario-texto");

    let sizes = document.getElementsByClassName("comment-size");

    inputs[index].style.display = "block";
    buttons[index].style.display = "block";
    options[index].style.display = "none";
    texts[index].style.display = "none";

    sizes[index].innerHTML = inputs[index].childNodes[1].value.length + "/280";
}

function onClickButtonEditar(id, index)
{
    //id es la clave primaria del comentario
    //index funciona para obtener el valor del input correspondiente al comentario a editar

    let inputs = document.getElementsByClassName("input-area");

    let texto = inputs[index].childNodes[1].value;
    showNotification("OK", "Se modificó el comentario de forma exitosa.");
    $(".swal2-confirm").click(function () {
        window.location.href = `/editar-comentario/${id}/${texto}`;
      });
}

function onEditInput(e, index)
{
    var buttonEnviar = document.getElementsByClassName('btn-editar');
    let boton = buttonEnviar[index]
    if (e.target.value.length == 0)
    {
        boton.disabled = true;
        boton.enabled = false;
    }
    else
    {
        boton.enabled = true;
        boton.disabled = false;
    }

    var commentSizeText  = document.getElementsByClassName('comment-size');
    commentSizeText[index].innerHTML = e.target.value.length + "/280";
}

function onClickNoSePresento(id)
{
    message = "Se registró con éxito el ausente del pasaje";
    showNotification("OK", message);
    $(".swal2-confirm").click(function () {
        window.location.href = `/no-se-presento/${id}`;
      });
}

// --- Listar pasajeros ---
function initializeListarPasajeros(estado)
{
    let estados = document.getElementsByClassName("estado-pasaje");

    for (let i = 0; i < estados.length; i++)
    {
        if (estados != null)
        {
            let estado = estados[i];
            setEstadoColor(estado);
        }
    }

    if (estado === "Pendiente")
        return;

    document.getElementById("combi-animation").setAttribute("class", "shake");

    if (estado === "Iniciado")
    {
        document.getElementById("combi").setAttribute("class", "combi-iniciado");
        return;
    }

    document.getElementById("combi").setAttribute("class", "combi-finalizado");
}

// --- Registro de diagnóstico ---

/*
let checkBoxFiebreUltimaSemana     = document.getElementById("checkBoxFiebreUltimaSemana");
let checkBoxPerdidaGustoUOlfato    = document.getElementById("checkBoxPerdidaGustoUOlfato");
let checkBoxDificultadRespiratoria = document.getElementById("checkBoxDificultadRespiratoria");
let checkBoxDolorDeGarganta        = document.getElementById("checkBoxDolorDeGarganta");
*/

function puedeRegistrarDiagnostico()
{
    document.getElementById("button-ok").style.display = "block";
    document.getElementById("button-rechazar").style.display = "none";

    document.getElementById("mensaje-sintomas").style.display = "none";
}

function puedeRechazarPasaje()
{
    document.getElementById("button-ok").style.display = "none";
    document.getElementById("button-rechazar").style.display = "block";

    document.getElementById("mensaje-sintomas").style.display = "block";
}

function onCheckBoxFiebreClick()
{
    let checkBoxFiebre = document.getElementById("checkBoxFiebre");
    let sintomas       = document.getElementById("sintomas");

    if (checkBoxFiebre.checked)
    {
        checkBoxFiebre.value = "True";
        sintomas.style.display = "none";

        puedeRechazarPasaje();

        return;
    }

    checkBoxFiebre.value = "False";
    sintomas.style.display = "block";

    puedeRegistrarDiagnostico();
}

function getCantidadDeSintomasSeleccionados(sintomas)
{
    let cantidad = 0;

    sintomas.forEach(function(sintoma){
        if (sintoma.checked)
            cantidad++;
    });

    return cantidad;
}

function onCheckBoxSintomaClick(index)
{
    sintomas = [document.getElementById("checkBoxFiebreUltimaSemana"),
                document.getElementById("checkBoxPerdidaGustoUOlfato"),
                document.getElementById("checkBoxDificultadRespiratoria"),
                document.getElementById("checkBoxDolorDeGarganta")];

     if (sintomas[index].checked)
        sintomas[index].value = "True";
     else
        sintomas[index].value = "False";

    //Si el pasajero tiene 2 o más sintomas entonces se habilita un botón para rechazarle el pasaje
    if (getCantidadDeSintomasSeleccionados(sintomas) >= 2)
        puedeRechazarPasaje();
    else
        puedeRegistrarDiagnostico();
}

// --- Alta de usuario express ---
function onLoadAltaUsuarioExpress(email)
{
    document.getElementById("email").value = email;
}


function onClickVenderPasajeExpress(viajeID)
{    
    let email = document.getElementById("email").value;

    $.ajax({
        url: `/vender-pasaje-express/${viajeID}/${email}`,
        dataType: 'json',
        success: function (data) {
            showNotification(data.result, data.message);

            if(data.result == "OK")
            {
                $(".swal2-confirm").click(function () {
                    window.location.href = `/listar-pasajeros/${viajeID}`;
                });
            }
        }
      });
}

function onClickRegistrarDiagnostico(pasajeID, viajeID)
{
    $.ajax({
        url: `/aceptar-pasaje/${pasajeID}`,
        dataType: 'json',
        success: function (data) {
            showNotification(data.result, data.message);

            $(".swal2-confirm").click(function () {
                window.location.href = `/listar-pasajeros/${viajeID}`;
            });
        }
      });
}

function onClickRechazarPasaje(pasajeID, viajeID)
{
    $.ajax({
        url: `/rechazar-pasaje/${pasajeID}`,
        dataType: 'json',
        success: function (data) {
            showNotification(data.result, data.message);

            $(".swal2-confirm").click(function () {
                window.location.href = `/listar-pasajeros/${viajeID}`;
            });
        }
      });
}