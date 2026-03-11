/**
 * @fileoverview Pure template functions for review request messages.
 * Each returns a ready-to-send string incorporating the business name,
 * customer name, service provided, and review link.
 */

export const TEMPLATES = {
  warm: (businessName, customerName, service, reviewLink) =>
    `Hey ${customerName}! 😊\n\n` +
    `Thank you so much for choosing ${businessName}` +
    `${service ? ` for your ${service}` : ''}! ` +
    `We absolutely loved having you and hope you had a great experience.\n\n` +
    `If you have a quick minute, it would mean the world to us if you could ` +
    `leave a short review — it really helps other people discover us! 🙏\n\n` +
    `${reviewLink}\n\n` +
    `Thanks again — we can't wait to see you next time!\n\n` +
    `Warmly,\n${businessName}`,

  concise: (businessName, customerName, service, reviewLink) =>
    `Hi ${customerName}, thanks for visiting ${businessName}` +
    `${service ? ` for ${service}` : ''}. ` +
    `We'd really appreciate a quick Google review if you have a moment. ` +
    `Here's the link:\n\n${reviewLink}\n\n` +
    `Thank you!\n${businessName}`,

  professional: (businessName, customerName, service, reviewLink) =>
    `Dear ${customerName},\n\n` +
    `Thank you for choosing ${businessName}` +
    `${service ? ` for your recent ${service}` : ''}. ` +
    `We hope the experience met your expectations.\n\n` +
    `Your feedback is invaluable to us. If you would be willing to share ` +
    `your experience in a brief Google review, we would be most grateful. ` +
    `You can do so at the following link:\n\n${reviewLink}\n\n` +
    `We appreciate your time and look forward to serving you again.\n\n` +
    `Kind regards,\n${businessName}`,
};
