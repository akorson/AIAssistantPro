// Handle login form submission
$('#loginForm').submit(function(event) {
    event.preventDefault();
    
    const email = $('#email').val();
  
    // Send login link to server
    $.post('/api/sendLoginLink', { email }, function(response) {
      alert('Login link has been sent to your email.');
    });
  });
  