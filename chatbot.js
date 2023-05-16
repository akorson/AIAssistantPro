const axios = require('axios')

async function notifyChatbot (email) {
  try {
    const chatbotUrl = 'https://api.example.com/chatbot/notify'
    await axios.post(chatbotUrl, { email })

    const zapierUrl = 'https://hooks.zapier.com/hooks/catch/1234567/abcde'
    await axios.post(zapierUrl, {
      phoneNumber: '3124682949',
      message: `Do you want to create a calendar event for the email with subject: "${email.subject}"?`
    })
  } catch (error) {
    console.error('Error notifying chatbot and sending text message:', error)
  }
}

const categories = {
  URGENT: [
    'worried',
    'concerned',
    'anxious',
    'urgent',
    'important',
    'taxes',
    'court',
    'cases',
    'ARDC'
  ],
  Leads: ['lead', 'leads'],
  Client_Communication: ['client communication'],
  Legal_Research: ['legal research'],
  Case_Management: ['case management'],
  Business_Development: ['business development'],
  Financial_Matters: ['financial matters'],
  Internal_Communication: ['internal communication'],
  Administrative_Matters: ['administrative matters'],
  Professional_Associations: ['professional associations'],
  Legal_Updates: ['legal updates'],
  Other: []
}

async function categorizeEmails (emails) {
  const categorizedEmails = []

  for (const email of emails) {
    email.category = 'Other'
    for (const [category, keywords] of Object.entries(categories)) {
      if (
        keywords.some(
          (keyword) =>
            email.body.includes(keyword) || email.subject.includes(keyword)
        )
      ) {
        email.category = category
        if (category === 'URGENT') {
          await notifyChatbot(email)
        }
        break
      }
    }
    categorizedEmails.push(email)
  }

  return categorizedEmails
}

module.exports = { categorizeEmails, notifyChatbot }
