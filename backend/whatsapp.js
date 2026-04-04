require('dotenv').config({ path: '../.env' });
const axios = require('axios');

const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
const ACCESS_TOKEN = process.env.META_ACCESS_TOKEN;

const getHeaders = () => ({
  Authorization: `Bearer ${process.env.META_ACCESS_TOKEN}`,
  'Content-Type': 'application/json'
});

const sendTextMessage = async (to, body) => {
  const token = process.env.META_ACCESS_TOKEN;
  const phoneId = process.env.WHATSAPP_PHONE_NUMBER_ID;
  if (!phoneId || !token) return;
  try {
    await axios.post(`https://graph.facebook.com/v18.0/${phoneId}/messages`, {
      messaging_product: 'whatsapp',
      recipient_type: 'individual',
      to,
      type: 'text',
      text: { body }
    }, { headers: getHeaders() });
  } catch (error) {
    console.error('Error sending message:', error.response?.data || error.message);
  }
};

const sendDocument = async (to, documentUrl, caption) => {
  const token = process.env.META_ACCESS_TOKEN;
  const phoneId = process.env.WHATSAPP_PHONE_NUMBER_ID;
  if (!phoneId || !token) return;
  try {
    await axios.post(`https://graph.facebook.com/v18.0/${phoneId}/messages`, {
      messaging_product: 'whatsapp',
      recipient_type: 'individual',
      to,
      type: 'document',
      document: { link: documentUrl, caption }
    }, { headers: getHeaders() });
  } catch (error) {
    console.error('Error sending document:', error.response?.data || error.message);
  }
};

const sendCTAMessage = async (to) => {
  const founderPhone = process.env.FOUNDER_PHONE || '+91XXXXXXXXXX';
  const ctaText = `Suno yaar, sabse best hoga ki Rocket bhai se ek baar seedha baat karo — woh 10 minute mein sab clear kar denge! 😊\n📞 Bas yeh button dabao aur directly unse baat karo:\n👉 Call Rocket Bhai: ${founderPhone}\nYa agar call nahi kar sakte abhi, toh apna preferred time batao — hum callback arrange kar denge! 🙏`;
  await sendTextMessage(to, ctaText);
};

const markAsRead = async (messageId) => {
  const token = process.env.META_ACCESS_TOKEN;
  const phoneId = process.env.WHATSAPP_PHONE_NUMBER_ID;
  if (!phoneId || !token) return;
  try {
    await axios.post(`https://graph.facebook.com/v18.0/${phoneId}/messages`, {
      messaging_product: 'whatsapp',
      status: 'read',
      message_id: messageId
    }, { headers: getHeaders() });
  } catch (error) {
    console.error('Error marking as read:', error.response?.data || error.message);
  }
};

module.exports = {
  sendTextMessage,
  sendDocument,
  sendCTAMessage,
  markAsRead
};
