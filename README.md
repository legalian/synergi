#synergi
<h1>IN-PROGRESS</h1>

commit test suck ass dick
ff
d
f
ff
<!-- https://developer.github.com/v3/git/commits/#create-a-commit -->
<!-- https://developer.github.com/v3/git/refs/#update-a-reference -->

<h1>TODO</h1>
-- make it so that when a pane is created or deleted it doesnt fuck up the sizes of all the other panes.
-- on the edit page make the file structure pane sized so you can see all of the file names, and it starts scrolled too far to the right
-- fix cursor bug when hovering over links. (files in edit page, delete project button, etc.)
-- git the most recent commit when loading session
-- beautify dropdown menus in browse
-- when a user requests a file or tries to make a change to a file, make sure they have joined the session they claim to be editing
	(it would be too much of a time sync to check with github for every little keystroke, so for each of those little changes we just check with our database to see if they have joined the session. They can only join the session if they have read permissions, so long as we implement the previous bullet point.)
-- update other database list to be an Array
-- fix css syntax error on todolist.html
-- add a versioning system on client side that mimics the server side- that way when the server rejects a change out of step with the client, they can come to a compromise or reload when the server and client can't find common ground.
-- make the client show some kind of message or attempt a reconnect when it gets a network error (if you close your laptop and come back you have to refresh to make things work again... this would be a source of confusion for users.)
-- improve client side code so everything works even if the server takes obnoxiously long to respond
-- rewrite project post request to be an ajax post instead of html form (todolist.html line 103)
-- need a better way to determine when someone really disconnects
	(currently, visiting and then refreshing the page sends two joins and then one disconnect.)
	(the first join adds you to the list of accessors, the second join does nothing, and the first diconnect removes them from the list of connected users even though theyre still connected and currently editing)
-- Doing a pull
	(button with pop-up settings. Not sure how this would work behind the scenes.)
-- Create a new branch
	(button with pop-up settings. This should change the branch column in every relevant place in our database.)
-- Allowing the user to make changes to the file structure
	(there's some magic behind the scenes with github api that i'm not totally sure about. A file move is a github operation that is different from deleting-and-creating a file.)
	(deleting and (possibly)creating files could also be a goal here but idk)
-- Pushing to github
	(with the push button and commit message dialogue)
	(pushes won't be able to be performed all the time- if someone pushes a change while they have the repo open in synergy, it's going to reject our push.)
	(if the commit+push cannot be performed, report the message back to the user so they can choose to either pull or make a new branch to resolve it.)
-- Automatically pushing to github and removing the session when there are no connected users
	(in the disconnect flask route, query for all sessions where connected users == "".)
	(if the push fails, because you have nobody to notify, just create a new branch with an automatically generated name to cram the users's changes. This should also change the branch column in the relevant database entries.)
	(there is a technical possibility that a user might hit the /join route but not the socket.join route, which would create a session where nobody ever connects in the first place. If you only clean up sessions when the last user disconnects, these will persist in our database indefinitely. Best way to clean these up is to query *all* ghost-town sessions when anyone disconnects.)


Stretch Goals
-- change filename from todolist to browse
-- invite system maybe





