/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.storm.mfp.metrics;

import com.esotericsoftware.kryo.io.Output;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Arrays;
import java.util.Collection;
import java.util.Map;
import org.apache.storm.metric.api.IMetricsConsumer;
import org.apache.storm.serialization.KryoValuesSerializer;
import org.apache.storm.task.IErrorReporter;
import org.apache.storm.task.TopologyContext;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.io.OutputStream;
import java.io.UnsupportedEncodingException;

import java.net.URLEncoder;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Listens for all metrics and POSTs them serialized to a configured URL.
 *
 * <p>To use, add this to your topology's configuration:
 * ```java
 *   conf.registerMetricsConsumer(HttpForwardingMetricsConsumer.class, "http://example.com:8080/metrics/my-topology/", 1);
 * ```
 *
 * <p>The body of the post is data serialized using {@link org.apache.storm.serialization.KryoValuesSerializer}, with the data passed in
 * as a list of `[TaskInfo, Collection&lt;DataPoint&gt;]`.  More things may be appended to the end of the list in the future.
 *
 * <p>The values can be deserialized using the org.apache.storm.serialization.KryoValuesDeserializer, and a correct config + classpath.
 *
 * <p>@see org.apache.storm.serialization.KryoValuesSerializer
 */
public class HttpForwardingMetricsConsumer implements IMetricsConsumer {
    public static final Logger LOG = LoggerFactory.getLogger(HttpForwardingMetricsConsumer.class);

    private transient URL url;
    private transient IErrorReporter errorReporter;
    private transient KryoValuesSerializer serializer;
    private transient String topologyId;

    @Override
    public void prepare(Map<String, Object> topoConf, Object registrationArgument, TopologyContext context, IErrorReporter errorReporter) { 
        try {
            url = new URL((String)registrationArgument);
            this.errorReporter = errorReporter;
            serializer = new KryoValuesSerializer(topoConf);
            topologyId = context.getStormId();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void handleDataPoints(TaskInfo taskInfo, Collection<DataPoint> dataPoints) {
        try {
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            try (OutputStream out = con.getOutputStream()) {
                String postData = buildJSONString(taskInfo, dataPoints);
                LOG.info(postData);
                out.write(postData.getBytes("UTF-8"));
                out.flush();
            }
            //The connection is not sent unless a response is requested
            int response = con.getResponseCode();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public String postData(String json) throws UnsupportedEncodingException{
        StringBuilder postData = new StringBuilder();
        postData.append("data=");
        postData.append(URLEncoder.encode(json, "UTF-8"));
        return postData.toString();
    }
    public String buildJSONString(TaskInfo taskInfo, Collection<DataPoint> dataPoints) {
        JSONObject meta = new JSONObject();
        meta.put("timestamp", taskInfo.timestamp);
        meta.put("srcWorkerHost", taskInfo.srcWorkerHost);
        meta.put("srcWorkerPort", taskInfo.srcWorkerPort);
        meta.put("srcTaskId", taskInfo.srcTaskId);
        meta.put("srcComponentId", taskInfo.srcComponentId);

        JSONArray metrics = new JSONArray();
        for (DataPoint p : dataPoints) {
            JSONObject metric = new JSONObject();
            metric.put("name", p.name);
            metric.put("value", p.value);
            metrics.add(metric);
        }

        JSONObject json = new JSONObject();
        json.put("meta", meta);
        json.put("metrics", metrics);

        return json.toString();
    }

    @Override
    public void cleanup() { }
}
