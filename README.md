#synergi
TODO
-- beautify dropdown menus in browse
-- md5 hash
	(update the database to also store the last few md5 hashes and deltas)
	(write a function server-side to "translate" one delta across another)
		(if their ranges overlap, return error, if the range of the one youre translating over preceeds the other's range, add data.length-amt.)
	(new changes require md5 hashes- if the md5 hash is not found, return error code)
-- stop the user from opening files that are too large
	(files that are too large should not be able to be added to our database.)
	(return an error code from /files post route instead of adding the file to the database)
	(github api might also have limits in place for how large of a file we can request- if github returns an error code for this case, we'd just need to pass the message along.)
-- when a user attempts to edit a project, we should check with github to make sure they have write permissions.
	(like yeah technically they aren't shown projects they dont have write permissions for but we never check for if they copy the url from someone who does, if there's a session already open)
	(return error code in /join and socket.join if theyre not allowed.)
-- when a user requests a file or tries to make a change to a file, make sure they have joined the session they claim to be editing
	(it would be too much of a time sync to check with github for every little keystroke, so for each of those little changes we just check with our database to see if they have joined the session. They can only join the session if they have read permissions, so long as we implement the previous bullet point.)

FUTURE TODO
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
-- mute sslv3 error




