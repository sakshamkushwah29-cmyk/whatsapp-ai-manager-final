const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(__dirname, '..', 'wedding_mediaaa.db');
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    city TEXT,
    wedding_date TEXT,
    status TEXT DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME,
    message_count INTEGER DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phone) REFERENCES leads(phone)
  );

  CREATE INDEX IF NOT EXISTS idx_messages_phone_time ON messages(phone, timestamp);
`);

module.exports = {
  upsertLead: (phone) => {
    const stmt = db.prepare(`
      INSERT INTO leads (phone, last_message_at, message_count) 
      VALUES (?, CURRENT_TIMESTAMP, 1)
      ON CONFLICT(phone) DO UPDATE SET 
        last_message_at = CURRENT_TIMESTAMP, 
        message_count = message_count + 1
    `);
    stmt.run(phone);
  },
  saveMessage: (phone, role, content) => {
    const stmt = db.prepare(`INSERT INTO messages (phone, role, content) VALUES (?, ?, ?)`);
    stmt.run(phone, role, content);
  },
  getConversation: (phone, limit = 20) => {
    const stmt = db.prepare(`SELECT * FROM messages WHERE phone = ? ORDER BY timestamp ASC LIMIT ?`);
    return stmt.all(phone, limit);
  },
  getAllLeads: () => {
    const stmt = db.prepare(`SELECT * FROM leads ORDER BY last_message_at DESC`);
    return stmt.all();
  },
  updateLeadStatus: (phone, status) => {
    const stmt = db.prepare(`UPDATE leads SET status = ? WHERE phone = ?`);
    stmt.run(status, phone);
  },
  updateLeadName: (phone, name) => {
    const stmt = db.prepare(`UPDATE leads SET name = ? WHERE phone = ?`);
    stmt.run(name, phone);
  }
};
