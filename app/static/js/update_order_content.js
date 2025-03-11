function updateOrderContent() {
    const ordersContainer = document.querySelector(".order-container");
    let url = ordersContainer.dataset.url;

    fetch(url)
    .then(response => response.text())
    .then(html => {
        ordersContainer.innerHTML = html; // Вставляем новый HTML
    })
    .catch(error => console.error("Ошибка загрузки:", error));
}

updateOrderContent();