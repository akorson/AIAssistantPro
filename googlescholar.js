const { google } = require('googleapis');
require('dotenv').config();

// Function to perform a Google Scholar search
async function googleScholarSearch(query) {
  const apiKey = process.env.API_KEY;

  // Create a custom search instance
  const customsearch = google.customsearch('v1');

  // Set the search parameters
  const params = {
    cx: process.env.SEARCH_ENGINE_ID,
    q: query,
    auth: apiKey,
  };

  try {
    // Perform the search
    const response = await customsearch.cse.list(params);

    // Extract the search results
    const results = response.data.items.map(item => ({
      title: item.title,
      link: item.link,
      snippet: item.snippet,
      authors: item.pagemap?.metatags[0]['citation_author'],
      year: item.pagemap?.metatags[0]['citation_year'],
    }));

    return results;
  } catch (error) {
    console.error('Error performing Google Scholar search:', error);
    return [];
  }
}

module.exports = { googleScholarSearch };
