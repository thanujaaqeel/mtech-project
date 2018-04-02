package org.apache.storm.mfp.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
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

public class MFPMinerBolt extends BaseRichBolt {
    private static final Logger LOG = LoggerFactory.getLogger(MFPMinerBolt.class);

    private OutputCollector collector;
    private AssocRuleMiner ruleMiner;
    private int minimumSupportLevel;

    public MFPMinerBolt(int minimumSupportLevel){
        this.minimumSupportLevel = minimumSupportLevel;
    }

    @Override
    public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
        this.collector = collector;
        this.ruleMiner = new Apriori();
        this.ruleMiner.setMinSupportLevel(minimumSupportLevel);
    }

    @Override
    public void execute(Tuple tuple) {
        delayBolt(tuple);
        List<List<String>> transactions = getTransactions(tuple);
        ItemSets mfpItemSets = findMaximalFrequentPatterns(transactions);
        emit(tuple, transactions, mfpItemSets);
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("size", "transactions", "item_sets"));
    }

    private void delayBolt(Tuple tuple){
        int delay = getDelay(tuple);
        if (delay < 1){
            return;
        }

        long startTime = System.currentTimeMillis();
        delayViaSleep(delay);
        long difference = (System.currentTimeMillis() - startTime);
        LOG.info("delayBolt: {}", difference);
    }
    private void delayViaSleep(int delay){
        Utils.sleep(delay);
    }

    private ItemSets findMaximalFrequentPatterns(List<List<String>> transactions){
        MetaData metaData = new MetaData(transactions);
        return ruleMiner.findMaxPatterns(transactions, metaData.getUniqueItems());
    }

    private void emit(Tuple tuple, List<List<String>> transactions, ItemSets mfpItemSets){
        int transactionsSize = transactions.size();
        String transactionsString = getTransactionsString(transactions);
        String itemSetsString = getItemSetsAsString(mfpItemSets);

        collector.emit(tuple, new Values(transactionsSize, transactionsString, itemSetsString));
        collector.ack(tuple);
        // LOG.info("Emitted {}", transactionsString);
    }

    private int getDelay(Tuple tuple){
        int delay = Integer.parseInt(tuple.getString(0).split("\t")[0]);
        return delay;
    }

    private List<List<String>> getTransactions(Tuple tuple){
        String[] rawTransactions = tuple.getString(0).split("\t");
        List<List<String>> transactions = new ArrayList<>();

        for (int i=1; i<rawTransactions.length; i++) {
            transactions.add(getTransaction(rawTransactions[i]));
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

    private List<String> getTransaction(String rawTransaction){
        String[] tokens = rawTransaction.split("\\s+");
        return Arrays.asList(tokens);
    }
}
