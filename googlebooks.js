const { google } = require('googleapis')
require('dotenv').config()

// Function to perform a Google Books search
async function googleBooksSearch (query) {
  const apiKey = process.env.API_KEY

  // Create a Google Books instance
  const books = google.books('v1')

  // Set the search parameters
  const params = {
    q: query,
    key: apiKey
  }

  try {
    // Perform the search
    const response = await books.volumes.list(params)

    // Extract the search results
    const results = response.data.items.map((item) => ({
      title: item.volumeInfo.title,
      authors: item.volumeInfo.authors,
      description: item.volumeInfo.description,
      link: item.volumeInfo.infoLink
    }))

    return results
  } catch (error) {
    console.error('Error performing Google Books search:', error)
    return []
  }
}

module.exports = { googleBooksSearch }
