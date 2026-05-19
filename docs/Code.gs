// ============================================================
// LB Marketing — Contact Form Handler
// Google Apps Script Web App
//
// SETUP INSTRUCTIONS (do this once):
// 1. Go to script.google.com → New project
// 2. Paste this entire file, replacing the default content
// 3. Update SPREADSHEET_ID below with your actual sheet ID
// 4. Click Deploy → New deployment
//    - Type: Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 5. Copy the Web App URL — paste it into contact.html as SCRIPT_URL
// ============================================================

const SPREADSHEET_ID = '1CdTwFxT11r-BBfoKjulwvtikV2TVsQaPO5-mcdQPOc4';
const SHEET_NAME = 'Sheet1'; // Default sheet name after CSV import

function doPost(e) {
  try {
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);

    const data = e.parameter;

    const row = [
      new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }),
      data.fname || '',
      data.lname || '',
      data.email || '',
      data.phone || '',
      data.business || '',
      data.website || '',
      data.vertical || '',
      data.tier || '',
      (data.challenges || '').replace(/,/g, ' | '), // join multiple challenges
      data.message || ''
    ];

    sheet.appendRow(row);

    // Optional: send email notification
    sendNotificationEmail(data);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Handle CORS preflight OPTIONS requests
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'LB Marketing form endpoint active' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function sendNotificationEmail(data) {
  // Optional — update this to your email address to get notified on each submission
  const NOTIFY_EMAIL = 'anthonyval@marketboostapp.com';

  const subject = `New Audit Request: ${data.business || 'Unknown Business'}`;
  const body = `
New contact form submission from lb-marketing site.

Name: ${data.fname} ${data.lname}
Email: ${data.email}
Phone: ${data.phone || 'Not provided'}
Business: ${data.business}
Website: ${data.website || 'Not provided'}
Industry: ${data.vertical}
Challenges: ${data.challenges || 'Not specified'}

Message:
${data.message || 'None'}

---
View all responses: https://docs.google.com/spreadsheets/d/${SPREADSHEET_ID}
  `.trim();

  try {
    MailApp.sendEmail(NOTIFY_EMAIL, subject, body);
  } catch (err) {
    // Email notification is optional — don't fail the submission if it errors
    console.log('Email notification failed:', err);
  }
}
