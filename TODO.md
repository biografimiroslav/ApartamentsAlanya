# TODO List for Phone Number Fix and Bot Enhancements

## Completed Tasks - Phone Number Fix
- [x] Modified setup_database.py to create phones table with single phone_number (no lang)
- [x] Updated app.py get_phone function to select phone_number without lang
- [x] Changed script.js loadPhoneFromDatabase to fetch without lang parameter
- [x] Updated updatePhoneNumber in script.js to target '.booking-phone' class
- [x] Deleted old database.db and ran setup_database.py to create new database structure
- [x] Verified database has the phone number entry

## Completed Tasks - Bot Enhancements
- [x] Added phone management functionality to bot (set_phone, process_phone_input)
- [x] Added reviews management functionality to bot (manage_reviews, add_review, delete_review, list_reviews)
- [x] Updated main menu to include phone and reviews buttons
- [x] Added process functions for phone and reviews input handling
- [x] Updated help text to include new features

## Remaining Tasks
- [ ] Restart the Flask application to load new code changes
- [ ] Test the phone number loading on the website
- [ ] Confirm phone number updates correctly in booking section
- [ ] Test bot phone management functionality
- [ ] Test bot reviews management functionality
- [ ] Ensure database tables for phones and reviews exist (check setup_database.py)

## Notes
- Database now has single phone number: '+38 (012) 345-67-89'
- Phone number is pulled from /api/phone endpoint without language dependency
- HTML uses class 'booking-phone' for the phone link in booking section
- Changes ensure one phone number across all pages regardless of language
- Bot now supports phone and reviews management via Telegram
- New bot features: change phone number, add/delete/list reviews
