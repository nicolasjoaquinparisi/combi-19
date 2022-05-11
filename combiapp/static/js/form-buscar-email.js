function getIcon(type)
{
    switch (type)
    {
        case "OK":
            return 'success';
        case "Error":
            return 'error';
        case "Warning":
            return 'warning';
        default:
            return null;
    }
}

function showNotification(type, message)
{
    let icon = getIcon(type);

    if (type === "OK")
        type = "Éxito";
    
    if (type === "Warning")
        type = "Atención";

    Swal.fire({
      icon: icon,
      title: type,
      text: message,
      confirmButtonColor: '#115571'
    })
}

function onFormRequestError()
{
    let response = {
        "result": "Error",
        "message": "Error en la conexión con el servidor."
    };
    showNotification(response.result, response.message);
}

function onFormSubmit(e)
{
    e.preventDefault();

    let req = new XMLHttpRequest();
    req.onload = function() {
        if (req.status === 200)
        {
            let data = JSON.parse(req.responseText);

            if (data.result === "OK")
            {
                document.getElementById("button-buscar-email").style.display = "none";
                document.getElementById("button-vender-pasaje").style.display = "block";
                document.getElementById("busqueda-exitosa").style.display = "block";
            }
            
            if (data.result === "Error")
            {
                showNotification(data.result, data.message);
                document.getElementById("busqueda-exitosa").style.display = "none";

                $(".swal2-confirm").click(function () {
                    window.location.href = "#";
                    });
            }
            
            if (data.result === "Warning")
            {
                showNotification(data.result, data.message);
                $(".swal2-confirm").click(function () {
                    window.location.href = `/alta-usuario-express/${data.viaje_id}/${data.email}`;
                    });
            }
        }
        else
        {
            onFormRequestError();
        }
    }
    req.onerror = function() {
        onFormRequestError();
    }

    req.open("post", "#");
    req.send(new FormData(e.target));
}

window.addEventListener("load", function() {
    let forms = document.querySelectorAll("form")
    for (let i = 0; i < forms.length; i++)
        forms[i].addEventListener("submit", onFormSubmit);
})

