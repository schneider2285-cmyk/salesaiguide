exports.handler = async (event) => {
  const headers = {
    "Access-Control-Allow-Origin": "https://salesaiguide.com",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Content-Type": "application/json",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers, body: JSON.stringify({ error: "Method not allowed" }) };
  }

  const apiKey = process.env.BEEHIIV_API_KEY;
  if (!apiKey) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: "Server configuration error" }) };
  }

  let email, utm_source, utm_medium;
  try {
    const data = JSON.parse(event.body);
    email = data.email;
    utm_source = data.utm_source || "salesaiguide";
    utm_medium = data.utm_medium || "website";
  } catch {
    return { statusCode: 400, headers, body: JSON.stringify({ error: "Invalid request" }) };
  }

  if (!email || !email.includes("@")) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: "Valid email required" }) };
  }

  try {
    const res = await fetch(
      "https://api.beehiiv.com/v2/publications/pub_6fb0289c-a5ac-4a9d-8f45-8a36b7e788ae/subscriptions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          email,
          reactivate_existing: true,
          send_welcome_email: true,
          utm_source,
          utm_medium,
        }),
      }
    );

    if (res.ok) {
      return { statusCode: 200, headers, body: JSON.stringify({ success: true }) };
    }

    const err = await res.text();
    console.error("Beehiiv API error:", res.status, err);
    return { statusCode: 502, headers, body: JSON.stringify({ error: "Subscription failed. Please try again." }) };
  } catch (e) {
    console.error("Network error:", e);
    return { statusCode: 502, headers, body: JSON.stringify({ error: "Service unavailable. Please try again." }) };
  }
};
