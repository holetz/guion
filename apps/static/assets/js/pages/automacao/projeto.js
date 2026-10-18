async function refreshQueue(queue_name) {
  const response = await fetch(`./carga/get_carga/${queue_name}`)
  const data = await response.json()
  element = $(`#table-${queue_name}`)
  element.DataTable().clear().destroy()
  element.DataTable({
    language: { url: "/static/assets/plugins/datatables/pt-BR.json" },
    buttons: ["copy", "excel", "print"],
    layout: { topStart: "buttons" },
    paging: false,
    columns: data["columns"].map((name) => ({
      title: name,
      data: name,
    })),
    scrollX: true,
    data: data["rows"],
  })
}

async function setCredencial(system) {
  const credencialRow = document.getElementById(`credencial-row-${system}`)
  const UserInput = credencialRow.querySelector('td:nth-child(2) input')
  const PasswordInput = credencialRow.querySelector('td:nth-child(3) input')
  const Button = credencialRow.querySelector('td:nth-child(4) button')

  const response = await fetch(
    `./set_credencial`, {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        system: system,
        username: UserInput.value,
        password: PasswordInput.value
      })
    }
  )
  const responseData = await response.json()

  showAlert(response.status, responseData.message)
  if (response.status == 200) {
    UserInput.setAttribute('start-value',UserInput.value)
    PasswordInput.value = ""
    Button.classList.add('btn-disabled')
    Button.classList.add('disabled')
    Button.classList.remove('btn-primary')
  }
}

async function refreshCredenciais() {
  const response = await fetch(`./get_credenciais`)
  const data = await response.json()
  const tableBody = document.getElementById("table-credenciais").getElementsByTagName("tbody")[0]

  for (const credencial of data) {
    const newRow = document.createElement('tr')
    newRow.id = `credencial-row-${credencial.system}`
    newRow.innerHTML = `
        <td><b>${credencial.system}</b></td>
        <td><input type="text" class="form-control" placeholder="Redefinir o usuário" start-value="${credencial.username}" value="${credencial.username}"></td>
        <td><input type="text" class="form-control" placeholder="Redefinir a senha"></td>
        <td><button onclick="setCredencial('${credencial.system}')" class="btn btn-disabled disabled">Salvar</button></td>
    `
    const UserInput = newRow.querySelector('td:nth-child(2) input')
    const PasswordInput = newRow.querySelector('td:nth-child(3) input')
    const Button = newRow.querySelector('td:nth-child(4) button')

    UserInput.addEventListener('input', function() {
      if (this.value != this.getAttribute('start-value')) {
          Button.classList.remove('btn-disabled')
          Button.classList.remove('disabled')
          Button.classList.add('btn-primary')
      } else {
        Button.classList.add('btn-disabled')
        Button.classList.add('disabled')
        Button.classList.remove('btn-primary')
      }
    });

    PasswordInput.addEventListener('input', function() {
      if (this.value) {
          Button.classList.remove('btn-disabled')
          Button.classList.remove('disabled')
          Button.classList.add('btn-primary')
      } else {
        Button.classList.add('btn-disabled')
        Button.classList.add('disabled')
        Button.classList.remove('btn-primary')
      }
    });

    tableBody.appendChild(newRow)
  }
}

async function refreshRelatorios() {
  const response = await fetch(`./carga/get_cargas`)
  const data = await response.json()

  element = $(`#table-relatorios`)
  element.DataTable().clear().destroy()
  element.DataTable({
    language: { url: "/static/assets/plugins/datatables/pt-BR.json" },
    buttons: ["copy", "excel", "print"],
    layout: { topStart: "buttons" },
    paging: false,
    columns: [
      {title: "ID", data: "id_carga"},
      {title: "Arquivo", data: "ds_arquivo"},
      {title: "Usuário", data: "username"},
      {title: "Data/Hora", data: "dt_carga"},
      {title: "Registros", data: "count_total"},
      {title: '<span class="fa-stack text-primary"><i class="far fa-square fa-stack-1x" style="font-size:20px"></i></span>', data: "count_pendente"},
      {title: '<span class="fa-stack text-success"><i class="far fa-square fa-stack-1x" style="font-size:20px"></i><i class="fa fa-check fa-stack-1x" style="font-size:15px"></i></span>', data: "count_concluido"},
      {title: '<span class="fa-stack text-danger"><i class="far fa-square fa-stack-1x" style="font-size:20px"></i><i class="fa fa-times fa-stack-1x" style="font-size:15px"></i></span>', data: "count_erro"},
      {
        title: 'Relatório',
        data: null,
        render: function(data, type, row) {
            return `<a href="./carga/get_relatorio/${row['id_carga']}"><button type="button" class="btn btn-block btn-primary btn-sm"><i class="fa fa-download"></i></button></a>`;
        }
      }
    ],
    data: data,
    order: [[0, 'desc']]

  })
}

async function clearQueueErrors() {
  try {
    const response = await fetch(`./carga/clear_carga_erros`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })

    const status = response.status
    const data = await response.json()
    showAlert(status, data.message)
  } catch (error) {
    console.error("Error:", error)
  } finally {
    updatePage()
    refreshQueue("erro")
  }
}

async function setQueue() {
  document.getElementById("importar-carga-input").click()
}

async function setQueueSubmit() {
  const fileInput = document.getElementById("importar-carga-input")
  if (fileInput.files.length > 0) {
    try {
      const form = document.getElementById("importar-carga-form")
      const formData = new FormData(form)
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
      })

      const status = response.status
      const data = await response.json()
      showAlert(status, data.message)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      refreshPage()
      refreshQueue("pendente")
      refreshQueue("concluido")
      refreshQueue("erro")
      refreshRelatorios()
    }
  }
}

async function sendCommand(action) {
  try {
    const response = await fetch(`./command/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })

    const status = response.status
    const data = await response.json()
    showAlert(status, data.message)
  } catch (error) {
    console.error("Error:", error)
  } finally {
    updatePage()
  }
}

async function updatePage() {
  const response = await fetch(`./get_info`)
  const data = await response.json()
  const status_color_classes = {
    Parado: "default",
    Parando: "default",
    Pausando: "warning",
    Pausado: "warning",
    Erro: "danger",
    Desconhecido: "default",
    Executando: "success",
    Aguardando: "info",
  }
  const color_classes = [
    "default",
    "warning",
    "danger",
    "success",
    "info",
    "blue",
  ]

  function formatAsPercentage(value) {
    return (value * 100).toFixed(2) + "%"
  }
  const status_color = status_color_classes[data["status"]] ?? "info"
  document.getElementById("info-name").textContent = data["name"]
  document.getElementById("info-description").textContent = data["description"]
  document.getElementById("info-sector").textContent = data["sector"]
  document.getElementById("info-system").textContent = data["system"]
  document.getElementById("info-id_projeto").textContent = id_projeto
  document.getElementById("info-rev_date").textContent = data["rev_date"]

  document.getElementById("carga-file").textContent =
    data["carga"]["ds_arquivo"]
  document.getElementById("carga-user").textContent = data["carga"]["username"]
  document.getElementById("carga-date").textContent = data["carga"]["dt_carga"]
  document.getElementById("carga-count").textContent =
    data["progress"]["Total"]

  document
    .getElementById("importar-carga-input")
    .setAttribute("accept", data["template_suffix"])
  document.getElementById(
    "carga-status"
  ).innerHTML = `<small class="badge badge-${status_color}">${data["status"]}</small>`

  document.getElementById("carga-pendente").textContent =
    data["progress"]["Pendente"] ?? 0
  document.getElementById("carga-concluido").textContent =
    data["progress"]["Concluído"] ?? 0
  document.getElementById("carga-erro").textContent =
    data["progress"]["Erro"] ?? 0

  const progress_bar = document.getElementById("carga-progress-bar")
  progress_bar.style.width = formatAsPercentage(data["progress"]["progress"])
  color_classes.forEach((cls) => {
    progress_bar.classList.remove(`bg-${cls}`)
  })
  progress_bar.classList.add(`bg-${status_color}`)
}

async function updateLog() {
  // if (document.getElementById('tabs-log-tab').getAttribute('aria-selected') === 'true') {
  const response = await fetch(`./get_log`)
  const data = await response.json()
  document.getElementById("log-stdout").textContent = data["stdout"]
  document.getElementById("log-stderr").textContent = data["stderr"]
  // }
}

async function loadPage() {
  refreshPage()
  refreshCredenciais()
  checkInput()
  setInterval(refreshPage, 3000);
  setInterval(checkInput, 3000);
  refreshQueue("pendente")
  refreshRelatorios()
}

async function refreshPage() {
  await updatePage()
  await updateLog()
}

const observer = new MutationObserver((mutationsList) => {
  for (const mutation of mutationsList) {
    if (
      mutation.type === "attributes" &&
      mutation.attributeName === "aria-selected"
    ) {
      if (mutation.target.getAttribute("aria-selected") === "true") {
        const tabName = mutation.target.id.split("-")[1]
        if (tabName == "relatorios") {refreshRelatorios()}
        else {refreshQueue(tabName)}
      }
    }
  }
})

observer.observe(document.getElementById("tabs-pendente-tab"), {
  attributes: true,
})
observer.observe(document.getElementById("tabs-concluido-tab"), {
  attributes: true,
})
observer.observe(document.getElementById("tabs-erro-tab"), {
  attributes: true,
})
observer.observe(document.getElementById("tabs-relatorios-tab"), {
  attributes: true,
})


function showAlert(status, message) {
  const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 5000,
  })

  if (status === 200) {
    Toast.fire({
      icon: "success",
      title: "Sucesso",
      text: message,
    })
  } else {
    Toast.fire({
      icon: "error",
      title: "Algo deu errado",
      text: message,
    })
  }
}

let checkInputRunning = false;
async function checkInput() {
  if (checkInputRunning) return

  checkInputRunning = true

  try {
    const response_get = await fetch(`./input/get_input`)
    const status_get = response_get.status
    
    if (status_get == 200) {
      const data_get = await response_get.json()
      const { value: input_response } = await Swal.fire({
        title: data_get.params.title,
        text: data_get.params.question,
        input: ('input' in data_get.params) ? data_get.params.input : "text",
        imageUrl: ('image' in data_get.params) ? `./static/${data_get.params.image}?${new Date().getTime()}` : "",
      })
      if (input_response) {
        
        const response_post = await fetch(
          `./input/set_response`, {
            method: "POST",
            headers: {'Content-Type': 'text/plain'},
            body: input_response
          }
        )
        const status_post = response_post.status
        if (status_post != 200) {
          const data_post = await response_post.json()
          showAlert(status_post, data_post.message)
        }
      }
    }
  } catch (error) {
    console.error("Error:", error)
  } finally {
    checkInputRunning = false
  }
}