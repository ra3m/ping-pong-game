Repo legend of my ping-pong game with two servers communicating via http.

To test out my code:

- clone repository
- create a virtual environment: python -m venv venv
- activate the virtual environment source venv/bin/activate
- install my dependencies: pip install -r requirements.txt

  on 3 diff terminals
  - terminal 1: python server1.py
  - terminal 2: python server2.py
  - terminal 3: python cli.py start 1000 (our test example, default is 4 seconds)

  Happy testing! :) watch how server 1 and 2 communicate, you can use this set of command cotrols: start, pause, resume, and stop.
