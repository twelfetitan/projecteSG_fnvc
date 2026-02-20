// Esperar a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", async () => {

    // 1. CARGAR LISTADO DE CLUBS
    // Llamada al endpoint para obtener los clubs (como en la imagen)
    const data = await fetch('http://localhost:8069/natacio/clubs/string')
        .then(r => r.json());

    console.log(data); // Mostrar datos en consola

    // Recorrer los clubs y añadirlos al div con id #clubs
    for (let club of data) {
        document.querySelector('#clubs').innerHTML += `<div>${club.name}</div>`;
    }

    // 2. CONFIGURAR BOTÓN DE PAGO
    // Escuchar el clic en el botón con id #pagar
    document.querySelector('#pagar').addEventListener('click', async () => {

        // Realizar la petición POST para pagar la cuota
        const response = await fetch('http://localhost:8069/natacio/pagar_quota', {
            method: 'POST',
            body: JSON.stringify({
                id: '1293' // ID fijo como en el ejemplo de la imagen
            })
        }).then(r => r.json());

        // Mostrar la respuesta en la consola
        console.log(response);

        // Opcional: Mostrar mensaje visual de éxito
        alert('Pago procesado para: ' + (response[0]?.name || 'Usuario 1293'));
    });

});
