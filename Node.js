const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');

const app = express();

// Check the Python version used by Node.js
exec('python3 --version', (error, stdout, stderr) => {
    if (error) {
        console.error(`Error: ${error.message}`);
        return;
    }
    console.log(`Python version: ${stdout || stderr}`);
});

const upload = multer({ dest: 'uploads/' });

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, 'public')));

// Route for file upload
app.post('/upload', upload.single('file'), (req, res) => {
    const filePath = path.join(__dirname, req.file.path);

    // Run Demucs command on uploaded file
    exec(`demucs -n mdx_extra_q ${filePath}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Demucs: ${error}`);
            return res.status(500).json({ error: 'Error processing file' });
        }

        // Handle Demucs output (e.g., save stems, send response)
        console.log(`Demucs output: ${stdout}`);
        console.log(`stderr: ${stderr}`);
        res.json({ message: 'File processed successfully', output: stdout });
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
