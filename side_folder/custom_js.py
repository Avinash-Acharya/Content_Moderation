JAVASCRIPT = """
<script>
document.querySelectorAll('a').forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        var url = link.href;
        // Send the URL to the input field and trigger a Gradio event
        fetch('/run_process_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        }).then(response => response.json())
        .then(data => {
            // Optionally handle the response
        });
    });
});
</script>
"""