
# OmniSight Manual Testing Checklist

## 1. Application Startup
- [ ] Application starts without errors.
- [ ] The home page loads successfully.
- [ ] No unexpected blank screen appears.
- [ ] Missing configuration is handled properly.

## 2. UI Testing
- [ ] All visible buttons respond to clicks.
- [ ] Input fields accept valid data.
- [ ] Empty input is handled correctly.
- [ ] Error messages are understandable.
- [ ] Page layout remains readable.

## 3. AI Self-Healing Testing
- [ ] The agent identifies the target webpage element.
- [ ] The agent handles a missing element gracefully.
- [ ] The recovery mechanism attempts to find an alternative locator.
- [ ] The result indicates whether recovery succeeded or failed.
- [ ] Invalid input does not cause an unhandled crash.

## 4. API Testing
- [ ] Valid requests return the expected response.
- [ ] Invalid requests are handled correctly.
- [ ] Missing required fields produce a clear error.
- [ ] API failures are reported clearly.

## 5. Test Execution Record

| Test Area | Status | Notes |
|---|---|---|
| Application Startup | Not Run | Pending execution |
| UI Testing | Not Run | Pending frontend verification |
| AI Self-Healing | Not Run | Pending model test |
| API Testing | Not Run | Pending API availability |

## Notes
- Mark a test as Passed only after verifying it.
- Record actual errors and steps to reproduce.
- Do not mark pending tests as passed.
