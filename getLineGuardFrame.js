const fs = require('fs');
const axios = require('axios');

async function getLineGuardFrame(color = 'gray', orientation = 'straight', camera_index = 0) {
    const url = `http://100.71.55.8:8000getLineGuardFrame?color=${color}&orientation=${orientation}&camera_index=${camera_index}`;

    try {
        const response = await axios.get(url, { responseType: 'arraybuffer' });
        fs.writeFileSync('line_guard_frame.png', response.data);
        console.log('Image saved as line_guard_frame.png');
    } catch (error) {
        console.error('Error fetching or saving image:', error.message);
    }
}

// Example usage
getLineGuardFrame();