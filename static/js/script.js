// Select elements 
const form = document.querySelector('form');
const input = document.querySelector('input');
const result = document.querySelector('#result');

// Listen for submit event
form.addEventListener('submit', event => {

  // Prevent default behavior
  event.preventDefault();

  // Get input value
  const ticker = input.value;

  // Clear previous results
  result.innerHTML = '';  

  // Show loading text
  const loading = document.createElement('p');
  loading.textContent = 'Analyzing...';
  result.appendChild(loading);

// AJAX request
fetch('/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: `ticker=${ticker}`  
})

  })
  .then(response => response.json())
  .then(data => {
    // Display analysis
    result.innerHTML = '';
    const analysis = document.createElement('p');
    analysis.textContent = data.analysis;
    result.appendChild(analysis);
  })
  .catch(error => {
    console.error(error);
    alert('Error fetching analysis');
  });

});
