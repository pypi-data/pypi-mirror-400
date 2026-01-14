# Procbench HTML Template

ProcBench is a process benchmarking tool that allows users to define test cases and run benchmarks on various processes.

A user specifies his test cases in JSON files, and ProcBench executes these test cases, collecting performance data.

Finally, ProcBench could output a report summarizing the results of the benchmarks, as a JSON file - we
shall call it the "results JSON file".

Now that ProcBench could run and output the results JSON file, we want to generate an HTML report from this results JSON file.

One results JSON file may contain the results of multiple test cases
that are all executed in a single run of ProcBench.

See [this file](../../result.json) to know the structure of the results JSON file.

**Now, you are going to generate the HTML template for ProcBench's output.**
The HTML template should reflect what is contained in the results JSON file.
Bootstrap CDN links could be used, though this is a single-file HTML so no
relative CSS/JS files should be used. The design should be lively instead
of raw styleless HTML elements.

Also, you must leave a placeholder in the HTML template
so that ProcBench could later fill in the actual data from the results JSON file into
the HTML template. Something like:

```html
<script>
    const testCasesData = [[TEST_CASES_DATA_PLACEHOLDER]];
</script>
```

And the HTML file must contain JS code down the road
to read the test cases and manipulate the DOM to show the data in a user-friendly way.

Also, make the test case sections collapse-able (collapsed by default),
and the samples could be viewed as tables in widgets
(also collapse-able and collapsed by default).

Now [do the work here](../html_template.html)
