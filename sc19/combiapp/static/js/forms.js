window.addEventListener("load", function() {
    selects = document.querySelectorAll("select")
    for (let i = 0; i < selects.length; i++)
    {
        sel = selects[i]
        value = sel.getAttribute("value")
        options = sel.querySelectorAll("option")
        for (let j = 0; j < options.length; j++)
        {
            opt = options[j]
            if (opt.getAttribute("value") === value)
                opt.setAttribute("selected", "true")
        }
    }
})