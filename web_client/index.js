// Usamos una función normal para evitar problemas de compatibilidad si los hubiera
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM Cargado");

    const btn = document.getElementById('pagar');
    const inputId = document.getElementById('swimmer-id');
    const statusMsg = document.getElementById('status-message');

    if (!btn) {
        console.error("No se encontró el botón con id 'pagar'");
        return;
    }

    // Listener para el botón
    btn.onclick = async function () {
        console.log("Click detectado");

        // Obtenemos la ID del input, si está vacío usamos '1293' (el de la imagen)
        const swimmerId = inputId.value || '1293';
        console.log("Procesando ID:", swimmerId);

        if (statusMsg) {
            statusMsg.innerHTML = "Procesando...";
            statusMsg.className = "info";
        }

        try {
            const response = await fetch('http://localhost:8069/natacio/pagar_quota', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: swimmerId })
            });

            const result = await response.json();
            console.log("Respuesta Odoo:", result);

            if (statusMsg) {
                if (response.ok && result.length > 0) {
                    statusMsg.innerHTML = "✅ Pago OK: " + result[0].name;
                    statusMsg.className = "success";
                } else {
                    statusMsg.innerHTML = "❌ Error: " + (result.error || "No encontrado");
                    statusMsg.className = "error";
                }
            }
        } catch (e) {
            console.error("Error Fetch:", e);
            alert("Error de conexión. ¿Está Odoo arrancado en el puerto 8069?");
        }
    };
});
