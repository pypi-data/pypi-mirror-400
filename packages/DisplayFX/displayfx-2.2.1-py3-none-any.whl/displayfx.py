class DisplayFx:
    def __init__(self, p_max_val, p_verbose=False, p_msg="", p_bar_len=50):
        self.bar_end_pos = 0
        self.bar_start_pos = 0
        self.bar_len = p_bar_len
        self.calibrate = 0
        self.leader_str = ""
        self.marker_len = 0
        self.markers = []
        self.marker_slice = 0
        self.max_val = p_max_val
        self.progress = 0
        self.silent = p_verbose
        self.msg = p_msg
        self.bar_len = max(self.bar_len, 20)
        self.leader_str = "{:.<{leaderLen}}".format("", leaderLen=self.bar_len)
        if self.max_val == 0:
            self.max_val = 1
            self.markers = ["100%"]
        elif self.max_val == 1:
            self.markers = ["100%"]
        elif self.max_val == 2:
            self.markers = ["50%", "100%"]
        elif self.max_val == 3:
            self.markers = ["33%", "67%", "100%"]
        elif self.max_val == 4:
            self.markers = ["25%", "50%", "75%", "100%"]
        else:
            self.markers = ["20%", "40%", "60%", "80%", "100%"]
        self.marker_qty = len(self.markers)
        self.marker_slice = self.bar_len / self.marker_qty
        # self.remInc = ( self.bar_len / self.marker_qty ) - self.marker_slice
        for i in range(self.marker_qty):
            self.marker_len = len(self.markers[i])
            self.bar_end_pos = round(self.marker_slice * (i + 1))
            self.leader_str = (
                self.leader_str[: self.bar_end_pos - self.marker_len]
                + self.markers[i]
                + self.leader_str[self.bar_end_pos :]
            )
        if self.max_val >= self.bar_len:
            self.marker_slice = self.bar_len / self.max_val
        if not self.silent:
            print(f"{self.msg}", end="", flush=True)
            if self.max_val == 0:
                print(self.leader_str)

    # end __init__

    def update(self, p_i):
        if not self.silent:
            # self.barCurrPos = 0
            if p_i == 0:
                self.calibrate = 1
            self.progress = (p_i + self.calibrate) / self.max_val
            self.bar_end_pos = round(self.progress * self.bar_len)
            if self.bar_end_pos > self.bar_start_pos:
                print(
                    self.leader_str[self.bar_start_pos : self.bar_end_pos],
                    end="",
                    flush=True,
                )
                self.bar_start_pos = self.bar_end_pos
                # self.marker_slice += self.marker_slice
            if p_i + self.calibrate == self.max_val:
                print()
