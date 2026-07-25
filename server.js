import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 3000;
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));
app.use('/audio', express.static(path.join(__dirname, 'data', 'audio')));
app.post('/api/chat', async (req, res) => {
    const { message } = req.body;
    if (!message)
        return res.status(400).json({ error: 'Message is required' });
    // Call Python bridge using the venv interpreter
    const python = spawn('venv_arisu/Scripts/python', ['src/arisu/api_bridge.py', message], {
        env: { ...process.env, PYTHONPATH: path.join(__dirname, 'src') }
    });
    let dataString = '';
    python.stdout.on('data', (data) => { dataString += data.toString(); });
    python.stderr.on('data', (data) => { console.error(`Python error: ${data}`); });
    python.on('close', (code) => {
        try {
            const match = dataString.match(/__ARISU_JSON__(\{[\s\S]*\})/);
            const payload = match ? match[1] : dataString.trim();
            const result = JSON.parse(payload);
            res.json(result);
        }
        catch (e) {
            console.error('Bridge error:', e);
            res.status(500).json({ error: 'Failed to process neural query', raw: dataString });
        }
    });
});
app.get('*', (_req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});
app.listen(Number(PORT), '0.0.0.0', () => {
    console.log(`ARISU Server running on port ${PORT}`);
});
