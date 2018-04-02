package org.apache.storm.mfp.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseWindowedBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;
import org.apache.storm.windowing.TupleWindow;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.storm.utils.Utils;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

import java.net.HttpURLConnection;
import java.net.URL;

import com.github.chen0040.fpm.AssocRuleMiner;
import com.github.chen0040.fpm.apriori.Apriori;
import com.github.chen0040.fpm.data.MetaData;
import com.github.chen0040.fpm.data.ItemSets;
import com.github.chen0040.fpm.data.ItemSet;

public class MFPMinerBolt extends BaseWindowedBolt {
    private static final Logger LOG = LoggerFactory.getLogger(MFPMinerBolt.class);

    private OutputCollector collector;
    private AssocRuleMiner ruleMiner;
    private int minimumSupportLevel;
    private int delay;

    public MFPMinerBolt(int minimumSupportLevel, int delay){
        this.minimumSupportLevel = minimumSupportLevel;
        this.delay = delay;
    }

    @Override
    public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
        this.collector = collector;
        this.ruleMiner = new Apriori();
        this.ruleMiner.setMinSupportLevel(minimumSupportLevel);
    }

    @Override
    public void execute(TupleWindow inputWindow) {
        // LOG.info("Executing tupleWindow {}", inputWindow);
        delayBolt();
        List<List<String>> transactions = getTransactions(inputWindow);
        ItemSets mfpItemSets = findMaximalFrequentPatterns(transactions);
        emit(transactions, mfpItemSets);
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("size", "transactions", "item_sets"));
    }

    private void delayBolt(){
        long startTime = System.currentTimeMillis();
        delayViaNetwork();
        long difference = (System.currentTimeMillis() - startTime);
        LOG.info("delayBolt: {}", difference);
    }
    private void delayViaSleep(){
        Utils.sleep(delay);
    }

    private void delayViaNetwork(){
        try {
            URL url = new URL("https://en.wikipedia.org/static/images/project-logos/enwiki-2x.png");
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");
            int response = con.getResponseCode();
        } catch (Exception e) {
            LOG.info("delayViaNetwork: {}", e.getMessage());
        }
    }

    private ItemSets findMaximalFrequentPatterns(List<List<String>> transactions){
        MetaData metaData = new MetaData(transactions);
        return ruleMiner.findMaxPatterns(transactions, metaData.getUniqueItems());
    }

    private void emit(List<List<String>> transactions, ItemSets mfpItemSets){
        int transactionsSize = transactions.size();
        String transactionsString = getTransactionsString(transactions);
        String itemSetsString = getItemSetsAsString(mfpItemSets);

        collector.emit(new Values(transactionsSize, transactionsString, itemSetsString));
        // LOG.info("Emitted {}", transactionsString);
    }

    private List<List<String>> getTransactions(TupleWindow tupleWindow){
        List<Tuple> tuplesInWindow = tupleWindow.get();
        List<List<String>> transactions = new ArrayList<>();

        for (Tuple tuple : tuplesInWindow) {
            transactions.add(getTransaction(tuple));
        }
        return transactions;
    }

    private String getTransactionsString(List<List<String>> transactions){
        StringBuilder builder = new StringBuilder();

        for(List<String> transaction : transactions){
          builder.append(String.join(" ", transaction));
          builder.append("\t");
        }
        return builder.toString();
    }

    private String getItemSetsAsString(ItemSets itemSets){
        StringBuilder builder = new StringBuilder();

        for(ItemSet itemSet : itemSets.getSets()){
          builder.append(itemSet.toString());
          builder.append("\t");
        }
        return builder.toString();
    }

    private List<String> getTransaction(Tuple tuple){
        String rawTransaction = (String) tuple.getValue(0);
        String[] tokens = rawTransaction.split("\\s+");
        return Arrays.asList(tokens);
    }
}
