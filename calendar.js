const axios = require('axios');

// Implement function to create a calendar event
async function createEvent(event, accessToken) {
  try {
    const calendarUrl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events';
    const headers = {
      'Authorization': `Bearer ${accessToken}`
    };
    const eventDetails = {
      summary: `Respond to email: ${event.email.subject}`,
      start: {
        dateTime: event.email.responseDue.toISOString(),
        timeZone: 'UTC',
      },
      end: {
        dateTime: new Date(event.email.responseDue.getTime() + 30 * 60 * 1000).toISOString(),
        timeZone: 'UTC',
      },
    };

    const response = await axios.post(calendarUrl, eventDetails, { headers });
    console.log('Calendar event created:', response.data);
  } catch (error) {
    console.error('Error creating calendar event:', error);
  }
}

async function checkUpcomingEvents(accessToken) {
  try {
    const currentTime = new Date().toISOString();
    const eventsUrl = `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${currentTime}&maxResults=10&singleEvents=true&orderBy=startTime`;
    const headers = {
      'Authorization': `Bearer ${accessToken}`
    };

    const response = await axios.get(eventsUrl, { headers });

    return response.data.items.map(event => ({
      id: event.id,
      summary: event.summary,
      start: event.start.dateTime || event.start.date,
    }));
  } catch (error) {
    console.error('Error fetching events:', error);
    return [];
  }
}

async function notifyUpcomingEvents(accessToken, sendMessage) {
  const events = await checkUpcomingEvents(accessToken);

  for (const event of events) {
    const eventTime = new Date(event.start).getTime();
    const now = new Date().getTime();
    const diffMinutes = (eventTime - now) / (1000 * 60);

    if (diffMinutes <= 10 && diffMinutes >= 0) {
      sendMessage(`Upcoming event: ${event.summary} - starting at ${event.start}`);
    }
  }
}

module.exports = {
  createEvent,
  checkUpcomingEvents,
  notifyUpcomingEvents
};
