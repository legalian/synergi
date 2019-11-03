#synergi
TODO
-- beautify dropdown menus in browse
-- when a user requests a file or tries to make a change to a file, make sure they have joined the session they claim to be editing
	(it would be too much of a time sync to check with github for every little keystroke, so for each of those little changes we just check with our database to see if they have joined the session. They can only join the session if they have read permissions, so long as we implement the previous bullet point.)

FUTURE TODO
-- update other database list to be an Array
-- fix css syntax error on todolist.html
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





