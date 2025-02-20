self.onmessage = async function(event) {
    const { SERVER_ADDRESS, win_name, lose_name, code, ID_NAME_DICT } = event.data;

    try {
        const response = await fetch(`${SERVER_ADDRESS}/save_score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                win_id: ID_NAME_DICT[win_name],
                lose_id: ID_NAME_DICT[lose_name],
                code: code
            })
        });
        // console.log(response);
        if (response.ok) {
            self.postMessage({ success: true, win_name });
        } else {
            self.postMessage({ success: false });
        }
    } catch (error) {
        self.postMessage({ error: error.message });
    }
};