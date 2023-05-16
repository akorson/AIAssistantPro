const axios = require('axios')
const { notifyChatbot } = require('./chatbot')

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

module.exports = { categorizeEmails }
