# TODO: Modify Review Modal Functionality

## Plan Summary
Modify the modal in `indexUA.html` so that when the user clicks "Відправити", the review is saved to the `reviews` table in the database and a notification is sent to the Telegram bot.

## Steps to Complete

1. **Add new endpoint in `app.py`**:
   - Create `/api/add_review` endpoint to handle saving new reviews.
   - Accept review text from frontend via POST request.
   - Save review to database using existing `add_review` function from `bot.py`.
   - Send notification to Telegram bot using bot's send_message function.

2. **Add notification function in `bot.py`**:
   - Create function to send notification to all admins when a new review is added.
   - Integrate this into the review saving process.

3. **Modify modal in `indexUA.html`**:
   - Update the submit button's click handler to send AJAX POST request to the new endpoint instead of showing alert.
   - Handle success/error responses from the server.

4. **Test the functionality**:
   - Run the Flask app and Telegram bot.
   - Submit a review through the modal and verify it's saved in the database and notification is sent.

## Progress
- [x] Step 1: Add new endpoint in `app.py`
- [x] Step 2: Add notification function in `bot.py`
- [x] Step 3: Modify modal in `indexUA.html`
- [ ] Step 4: Test the functionality
