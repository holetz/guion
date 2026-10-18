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

async function sendCommand(id_projeto, action) {
  try {
    const response = await fetch(`/automacao/projeto/${id_projeto}/command/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })

    const status = response.status
    const data = await response.json()
    showAlert(status, data.message)
  } catch (error) {
    console.error("Error:", error)
  } finally {
    updateTable()
  }
}

async function updateTable() {
  try {
    const response = await fetch("/automacao/projetos/get_info");
    const data = await response.json();
    const status_color_classes = {
        "Parado": "default",
        "Parando": "default",
        "Pausando": "warning",
        "Pausado": "warning",
        "Erro": "danger",
        "Desconhecido": "default",
        "Executando": "success",
        "Aguardando": "info"
    };
    const color_classes = [
        "default",
        "warning",
        "danger",
        "success",
        "info",
        "blue"
    ]

    function formatAsPercentage(value) {
    return (value * 100).toFixed(2) + '%';
    }

    for (const id_projeto in data) {
        
      const row = document.getElementById(`row-${id_projeto}`);
      const status_color = status_color_classes[data[id_projeto]['status']] ?? "info"

      if (row) {
        row.querySelector(".col-name").innerHTML = `<a href="./projeto/${id_projeto}">${data[id_projeto]["name"]}</a><br /><small>Revisado em: ${data[id_projeto]["rev_date"]}</small>`;
        row.querySelector(".col-status").innerHTML = `<small class="badge badge-${status_color}">${data[id_projeto]['status']}</small>`
        row.querySelector(".col-sector").textContent = data[id_projeto]["sector"];
        row.querySelector(".col-system").textContent = data[id_projeto]["system"];
        
        row.querySelector(".var-progress-bar-label").textContent = formatAsPercentage(data[id_projeto]['progress']);
        const progress_bar = row.querySelector(".progress-bar")
        progress_bar.style.width = formatAsPercentage(data[id_projeto]['progress']);
        color_classes.forEach(cls => {progress_bar.classList.remove(`bg-${cls}`);});
        progress_bar.classList.add(`bg-${status_color}`);
      }
    }
  } catch (error) {
    console.error("Erro ao atualizar a tabela:", error);
  }
}

async function loadPage() {
  updateTable()
  setInterval(updateTable, 3000);
}