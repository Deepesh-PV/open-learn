document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })  // Must match FastAPI model keys
    });

    if (response.status === 200) {
      // If status code is 200 (OK), login was successful
      const data = await response.json();  // Parse the response as JSON
      console.log("Login successful:", data);
      
      // Redirect to the next page after successful login
      window.location.href = "/course_window.html";  // Change this to your next page's URL
    } else {
      // Handle non-200 status codes (e.g., unauthorized or errors)
      throw new Error("Login failed, please check your credentials.");
    }
  } catch (error) {
    console.error("Error:", error.message);
    alert(error.message); // Show error message to the user
  }
});
