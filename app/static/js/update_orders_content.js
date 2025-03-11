function updateOrdersContent(url) {
    const ordersContainer = document.querySelector(".orders-container");

    fetch(url)
    .then(response => response.text())
    .then(html => {
        ordersContainer.innerHTML = html;
    })
    .catch(error => console.error("Ошибка загрузки:", error));
}

const baseUrl = window.location.origin;

const url = `${baseUrl}/orders_template`;

updateOrdersContent(url);