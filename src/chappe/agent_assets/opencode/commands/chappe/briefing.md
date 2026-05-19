RUN chappe bootstrap --channel $ARGUMENTS
RUN chappe doctor
RUN chappe briefing $ARGUMENTS --period 90d --budget tokens:12000

Summarize the JSON output into channel signals; audience demand; top posts; next commands.
