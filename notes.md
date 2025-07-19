endpoint for accounts
http://localhost:8000/api/accounts/users/

endpoint for academics
http://localhost:8000/api/academics/classes/

endpoint for assessment
http://localhost:8000/api/assessment/tests/

endpoint for announcement
http://localhost:8000/api/announcement/

GET    /api/assessment/grades/     - List all
POST   /api/assessment/grades/     - Create new
GET    /api/assessment/grades/1/   - Retrieve one
PUT    /api/assessment/grades/1/   - Update
PATCH  /api/assessment/grades/1/   - Partial update
DELETE /api/assessment/grades/1/   - Delete

Admin: http://localhost:8000/admin/
API Root: http://localhost:8000/api/assessment/
JWT Token: http://localhost:8000/api/token/
Schema: http://localhost:8000/api/schema/
Docs UI: http://localhost:8000/api/docs/

Events:
GET /api/events/events/ - List all events
POST /api/events/events/ - Create new event (admin/teacher only)
GET /api/events/events/<id>/ - Get specific event
PUT/PATCH /api/events/events/<id>/ - Update event
DELETE /api/events/events/<id>/ - Delete event

Participants:
GET /api/events/participants/ - List participants
POST /api/events/participants/ - Register participant
GET /api/events/participants/<id>/ - Get specific participant
PUT/PATCH /api/events/participants/<id>/ - Update participation
DELETE /api/events/participants/<id>/ - Remove participant