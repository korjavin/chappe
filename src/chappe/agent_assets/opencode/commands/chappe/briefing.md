RUN chappe bootstrap --channel $ARGUMENTS
RUN chappe doctor
RUN chappe briefing $ARGUMENTS --period 90d --budget tokens:12000

Summarize the JSON output into growth opportunities, audience demand, top posts, and next commands.
