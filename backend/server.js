require('dotenv').config({ path: '../.env' });
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const db = require('./db');
const agent = require('./agent');
const whatsapp = require('./whatsapp');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Set up brochure upload (Vercel uses /tmp)
const uploadDir = os.environ.get('VERCEL') ? '/tmp' : path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Serve brochure
app.use('/brochure.pdf', express.static(path.join(uploadDir, 'brochure.pdf')));

const storage = multer.diskStorage({
  destination: uploadDir,
  filename: (req, file, cb) => {
    cb(null, 'brochure.pdf');
  }
});
const upload = multer({ storage });

// Webhook Verification (GET)
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === process.env.WEBHOOK_VERIFY_TOKEN) {
    console.log('WEBHOOK_VERIFIED');
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});

// Receive Messages (POST)
app.post('/webhook', async (req, res) => {
  const body = req.body;
  if (body.object) {
    if (body.entry && body.entry[0].changes && body.entry[0].changes[0] && body.entry[0].changes[0].value.messages && body.entry[0].changes[0].value.messages[0]) {
      const message = body.entry[0].changes[0].value.messages[0];
      const from = message.from;
      const type = message.type;
      
      let messageText = '';
      if (type === 'text') {
        messageText = message.text.body;
      } else if (type === 'image') {
        messageText = '[Image Received]';
      } else if (type === 'document') {
        messageText = '[Document Received]';
      } else if (type === 'audio') {
        messageText = '[Audio Received]';
      } else if (type === 'button') {
        messageText = message.button.text;
      }
      
      if (messageText) {
        await agent.handleIncomingMessage(from, messageText, type);
        await whatsapp.markAsRead(message.id);
      }
    }
    res.sendStatus(200);
  } else {
    res.sendStatus(404);
  }
});

// --- ADMIN API ENDPOINTS ---

app.get('/health', (req, res) => {
  const connected = !!(process.env.WHATSAPP_PHONE_NUMBER_ID && process.env.META_ACCESS_TOKEN);
  res.json({ status: 'ok', whatsappConnected: connected });
});

app.post('/admin/upload-brochure', upload.single('file'), (req, res) => {
  res.json({ status: 'success', message: 'Brochure uploaded successfully.' });
});

app.get('/admin/leads', async (req, res) => {
  try {
    const leads = await db.getAllLeads();
    res.json(leads);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/admin/conversation/:phone', async (req, res) => {
  try {
    const history = await db.getConversation(req.params.phone, 100);
    res.json(history);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/admin/send-manual', async (req, res) => {
  try {
    const { phone, message } = req.body;
    await whatsapp.sendTextMessage(phone, message);
    await db.saveMessage(phone, 'assistant', message);
    res.json({ status: 'success' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/admin/update-status', async (req, res) => {
  try {
    const { phone, status } = req.body;
    await db.updateLeadStatus(phone, status);
    res.json({ status: 'success' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

if (process.env.NODE_ENV !== 'production') {
  app.listen(PORT, () => {
    console.log(`Backend server running on port ${PORT}`);
  });
}

module.exports = app;
