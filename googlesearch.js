const { google } = require('googleapis')
require('dotenv').config()

// Function to perform a Google search
async function googleSearch (query) {
  const searchEngineId = process.env.SEARCH_ENGINE_ID
  const apiKey = process.env.API_KEY

  // Create a custom search instance
  const customsearch = google.customsearch('v1')

  // Set the search parameters
  const params = {
    cx: searchEngineId,
    q: query,
    auth: apiKey
  }

  try {
    // Perform the search
    const response = await customsearch.cse.list(params)

    // Extract the search results
    const results = response.data.items.map((item) => ({
      title: item.title,
      link: item.link,
      snippet: item.snippet
    }))

    return results
  } catch (error) {
    console.error('Error performing Google search:', error)
    return []
  }
}

module.exports = { googleSearch }
